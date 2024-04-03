import typing
import pandas as pd

from data.raw import RawData
from utils.album import short_album_name
from utils.date import release_year
from utils.machine_learning import prepare_ml_data
from utils.record_label import standardize_record_labels
from utils.util import first
from utils.artist_relationship import producer_credit_types

class DataProvider:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataProvider, cls).__new__(cls)
            cls._instance._initialized = False

        return cls._instance
    

    def __init__(self):
        if self._initialized:
            return
        
        self._artists = None
        self._albums = None
        self._owned_albums = None
        self._playlists = None
        self._tracks = None
        self._owned_tracks = None

        self._album_label = None
        self._album_artist = None
        self._playlist_track = None
        self._track_artist = None
        self._artist_genre = None
        self._track_genre = None
        self._genres_with_page = None
        self._track_artist = None
        self._liked_tracks_sample = None
        self._ml_data = None
        self._track_credits = None
        self._producers_with_page = None
        self._current_track_scores = None
        self._track_scores_over_time = None
        self._owned_track_uris = None
        self._owned_album_uris = None

        self._initialized = True


    def playlist(self, uri: str) -> pd.Series:
        return self.playlists(uris={uri}).iloc[0]
    

    def playlists(self, 
                  uris: typing.Iterable[str] = None, 
                  track_uri: str = None, 
                  album_uri: str = None,
                  artist_uri: str = None) -> pd.DataFrame:
        raw = RawData()
        playlist_track = raw['playlist_track']

        if self._playlists is None:
            playlist_track_full = pd.merge(playlist_track, self.tracks(), on='track_uri')
            track_counts = playlist_track_full\
                .groupby("playlist_uri")\
                .agg({"track_uri": "count", "track_liked": "sum"})\
                .reset_index()\
                .rename(columns={"track_uri": "playlist_track_count", "track_liked": "playlist_track_liked_count"})
            
            self._playlists = pd.merge(raw['playlists'], track_counts, on='playlist_uri')

        out = self._playlists

        if uris is not None:
            out = out[out['playlist_uri'].isin(uris)]

        if track_uri is not None:
            uris = set(playlist_track[playlist_track['track_uri'] == track_uri]['playlist_uri'])
            out = out[out['playlist_uri'].isin(uris)]

        if album_uri is not None:
            track_uris = set(self.tracks(album_uri=album_uri)['track_uri'])
            uris = set(playlist_track[playlist_track['track_uri'].isin(track_uris)]['playlist_uri'])
            out = out[out['playlist_uri'].isin(uris)]

        if artist_uri is not None:
            track_uris = set(self.tracks(artist_uri=artist_uri)['track_uri'])
            uris = set(playlist_track[playlist_track['track_uri'].isin(track_uris)]['playlist_uri'])
            out = out[out['playlist_uri'].isin(uris)]

        return out


    def albums(self, uris: typing.Iterable[str] = None, owned = False) -> pd.DataFrame:
        if self._albums is None:
            raw = RawData()
            albums = raw["albums"].copy()
            albums['album_release_year'] = albums['album_release_date'].apply(release_year)
            albums['album_short_name'] = albums['album_name'].apply(short_album_name)
            self._albums = albums
            self._owned_albums = albums[albums['album_uri'].isin(self.__owned_album_uris())]
        
        out = self._owned_albums if owned else self._albums

        if uris is not None:
            out = out[out["album_uri"].isin(uris)]
        
        return out
    

    def track(self, uri: str):
        return self.tracks(uris=[uri]).iloc[0]
        

    def tracks(self, 
               uris: typing.Iterable[str] = None, 
               liked: bool = None, 
               label: str = None, 
               genre: str = None, 
               album_uri: str = None, 
               playlist_uri: str = None,
               artist_uri: str = None,
               owned: bool = False) -> pd.DataFrame:
        raw = RawData()

        if self._tracks is None:
            tracks = pd.merge(raw["tracks"], raw["audio_features"], on="track_uri")
            tracks = pd.merge(tracks, self.albums(), on="album_uri")

            liked_track_uris = set(raw["liked_tracks"]["track_uri"])
            tracks["track_liked"] = tracks["track_uri"].isin(liked_track_uris)

            artists = add_primary_prefix(self.artists().copy())
            track_artist = raw['track_artist']
            track_primary_artist = track_artist[track_artist['artist_index'] == 0][['track_uri', 'artist_uri']]
            track_primary_artist.rename(columns={'artist_uri': 'primary_artist_uri'}, inplace=True)

            scores = self.__aggregate_track_scores()

            tracks = pd.merge(tracks, track_primary_artist, on="track_uri")
            tracks = pd.merge(tracks, artists, on="primary_artist_uri")
            tracks = pd.merge(tracks, scores, on='track_uri', how="left")
            tracks['track_score'].fillna(0, inplace=True)

            self._tracks = tracks
            self._owned_tracks = tracks[tracks['track_uri'].isin(self.__owned_track_uris())]

        out = self._owned_tracks if owned else self._tracks

        if uris is not None:
            out = out[out["track_uri"].isin(uris)]

        if liked is not None:
            out = out[out["track_liked"] == liked]

        if label is not None:
            if self._album_label is None:
                self._album_label = standardize_record_labels(self.albums(), self.tracks())

            albums_uris = self._album_label[self._album_label["album_standardized_label"] == label]["album_uri"]
            out = out[out['album_uri'].isin(albums_uris)]

        if genre is not None:
            track_genre = self.track_genre()
            tracks_in_genre = set(track_genre[track_genre['genre'] == genre]['track_uri'])
            out = out[out["track_uri"].isin(tracks_in_genre)]

        if album_uri is not None:
            out = out[out['album_uri'] == album_uri]

        if playlist_uri is not None:
            playlist_track = raw['playlist_track']
            track_uris = set(playlist_track[playlist_track['playlist_uri'] == playlist_uri]['track_uri'])
            out = out[out["track_uri"].isin(track_uris)]

        if artist_uri is not None:
            track_artist = raw['track_artist']
            track_uris = set(track_artist[track_artist['artist_uri'] == artist_uri]['track_uri'])
            out = out[out["track_uri"].isin(track_uris)]

        return out
    

    def track_credits(self, 
                      track_uris: typing.Iterable[str] = None, 
                      artist_uri: str = None, 
                      artist_mbids: typing.Iterable[str] = None, 
                      include_aliases: bool = False, 
                      credit_types: typing.Iterable[str] = None) -> pd.DataFrame:
        if self._track_credits is None:
            rd = RawData()

            track_credits = pd.merge(rd['mb_recording_credits'], rd['mb_recordings'], on="recording_mbid")
            track_credits = pd.merge(track_credits, rd['mb_artists'], on="artist_mbid")
            track_credits = pd.merge(track_credits, rd['sp_artist_mb_artist'], how="left", on="artist_mbid")
            track_credits = pd.merge(track_credits, rd['sp_track_mb_recording'], how="left", on="recording_mbid")
            track_credits = pd.merge(track_credits, self.artists(), how="left", left_on="spotify_artist_uri", right_on="artist_uri")
            track_credits = pd.merge(track_credits, self.tracks(), how="left", left_on="spotify_track_uri", right_on="track_uri")
            track_credits['producer_has_page'] = track_credits['artist_mbid'].isin(self.producers_with_page())

            self._track_credits = track_credits

        out = self._track_credits

        if track_uris is not None:
            out = out[out["track_uri"].isin(track_uris)]

        if artist_uri is not None:
            if include_aliases:
                alias_mbids = self._artist_mbids_with_aliases(artist_uri=artist_uri)
                if alias_mbids is None:
                    out = out[out["artist_uri"] == artist_uri]
                else:
                    out = out[out['artist_mbid'].isin(alias_mbids)]
            else:
                out = out[out["artist_uri"] == artist_uri]

        if artist_mbids is not None:
            with_aliases = set()
            for mbid in artist_mbids:
                with_aliases = with_aliases.union(self._artist_mbids_with_aliases(artist_mbid=mbid))
            out = out[out["artist_mbid"].isin(artist_mbids)]

        if credit_types is not None:
            out = out[out["credit_type"].isin(credit_types)]

        return out.copy()
    

    def _artist_mbids_with_aliases(self, artist_uri: str = None, artist_mbid: str = None):
        if artist_uri is None and artist_mbid is None:
            return set()
        
        raw = RawData()
        if artist_uri is not None and artist_mbid is None:
            artist_join = raw['sp_artist_mb_artist']
            if artist_uri not in set(artist_join['spotify_artist_uri']):
                return set()

            own_mbid = artist_join[artist_join['spotify_artist_uri'] == artist_uri].iloc[0]['artist_mbid']
            if own_mbid is None:
                return set()
        else:
            own_mbid = artist_mbid
        
        
        alias_relationships = {'is person', 'artist_rename'}
        relationships = raw['mb_artist_relationships']
        forward_aliases = relationships[
                            (relationships['artist_mbid'] == own_mbid) & 
                            (relationships['relationship_type'].isin(alias_relationships))
                        ]['other_mbid']
        backward_aliases = relationships[
                            (relationships['other_mbid'] == own_mbid) & 
                            (relationships['relationship_type'].isin(alias_relationships))
                        ]['artist_mbid']

        return {own_mbid}.union(forward_aliases).union(backward_aliases)
    

    def top_tracks(self, 
                   current: bool = None, 
                   top: int = None, 
                   min_occurrences: int = None, 
                   term: str = None, 
                   track_uris: typing.Iterable[str] = None) -> pd.DataFrame:
        out = RawData()['top_tracks']

        if term is not None:
            out = out[out['term'] == term]

        if min_occurrences is not None:
            grouped = out.groupby('track_uri').agg({'as_of_date': 'count'}).reset_index()
            grouped = grouped[grouped['as_of_date'] >= min_occurrences]
            uris = grouped['track_uri'].unique()
            out = out[out['track_uri'].isin(uris)]
            
        if current:
            if len(out) == 0:
                return out
            
            most_recent_date = out['as_of_date'].iloc[0]
            out = out[out['as_of_date'] == most_recent_date]
            out = out.drop(columns=['as_of_date'])

        if top is not None:
            out = out[out['index'] <= top]

        if track_uris is not None:
            out = out[out['track_uri'].isin(track_uris)]

        return out.copy()
    

    def track_scores_over_time(self):
        if self._track_scores_over_time is None:
            out = None

            print('Calculating track scores over time...')
            for as_of_date in self.top_tracks()['as_of_date'].unique():
                print('    ' + as_of_date + '...')
                scores = self.__aggregate_track_scores(as_of=as_of_date)
                scores['as_of_date'] = as_of_date
                out = scores if out is None else pd.concat([out, scores])
            self._track_scores_over_time = out.reset_index()
            print('Done!')

        return self._track_scores_over_time
    

    def __aggregate_track_scores(self, as_of: str=None):
        if as_of is None and self._current_track_scores is not None:
            return self._current_track_scores
        
        top = self.top_tracks()

        if as_of is not None:
            top = top[top['as_of_date'] <= as_of]

        top['track_score'] = top.apply(lambda row: placement_score(row['index'], row['term']), axis=1)

        out = top.groupby('track_uri')\
            .agg({'track_score': 'sum'})\
            .reset_index()
        
        out = out.sort_values('track_score', ascending=False)

        out['track_score_rank'] = [i + 1 for i in range(len(out))]

        if as_of is None and self._current_track_scores is None:
            self._current_track_scores = out

        return out


    def ml_data(self, track_uris: typing.Iterable[str] = None):
        if self._ml_data is None:
            self._ml_data = prepare_ml_data(self.tracks(), self.track_genre(), self.album_label())

        out = self._ml_data

        if track_uris is not None:
            track_uris = [uri for uri in track_uris if uri in out.index]
            out = out.loc[track_uris]

        return out
    
    
    def liked_tracks_sample(self):
        if self._liked_tracks_sample is None:
            self._liked_tracks_sample = self.tracks(liked=True)
            if len(self._liked_tracks_sample) > 200:
                self._liked_tracks_sample = self._liked_tracks_sample.sample(200, random_state=0)
        return self._liked_tracks_sample


    def primary_artist(self, track_uri: str) -> pd.Series:
        track_artist = RawData()['track_artist']
        artist_uri = track_artist[(track_artist['track_uri'] == track_uri) & (track_artist['artist_index'] == 0)].iloc[0]['artist_uri']
        return self.artist(artist_uri)
    

    def artist(self, uri: str = None, mbid: str = None) -> pd.Series:
        if uri is not None:
            return self.artists(uris={uri}).iloc[0]
        
        if mbid is not None:
            return self.artists(mbids={mbid}).iloc[0]
        
        return None
    

    def artists(self, 
                uris: typing.Iterable[str] = None, 
                mbids: typing.Iterable[str] = None,
                with_page: bool = None, 
                track_uri: str = None,
                album_uri: str = None) -> pd.DataFrame:
        raw = RawData()
        if self._artists is None:
            track_artist = raw['track_artist']
            artist_liked_tracks = pd.merge(track_artist, raw["liked_tracks"], on="track_uri")\
                .groupby("artist_uri")\
                .agg({"track_uri": "count"})\
                .reset_index()
            artist_liked_tracks.rename(columns={"track_uri": "artist_liked_track_count"}, inplace=True)
            artist_all_track_counts = track_artist[["artist_uri", "track_uri"]]\
                .groupby("artist_uri")\
                .agg({"track_uri": "count"})\
                .reset_index()
            artist_all_track_counts.rename(columns={"track_uri": "artist_track_count"}, inplace=True)
            artist_track_counts = pd.merge(artist_liked_tracks, artist_all_track_counts, how="outer", on="artist_uri")
            
            artists = pd.merge(raw['artists'], artist_track_counts, on="artist_uri", how="outer")
            artists['artist_track_count'].fillna(0, inplace=True)
            artists['artist_liked_track_count'].fillna(0, inplace=True)
            
            artists["artist_has_page"] = (artists["artist_track_count"] >= 50) \
                | ((artists["artist_track_count"] >= 10) & (artists["artist_liked_track_count"] > 0)) \
                | (artists["artist_liked_track_count"] >= 5)

            self._artists = artists

        out = self._artists

        if mbids is not None:
            mb_join = raw['sp_artist_mb_artist']
            matching_uris = mb_join[mb_join['artist_mbid'].isin(mbids)]['spotify_artist_uri']
            uris = set(uris or {}) + set(matching_uris)

        if uris is not None:
            out = out[out['artist_uri'].isin(uris)]

        if with_page is not None:
            out = out[out['artist_has_page'] == with_page]

        if track_uri is not None:
            track_artist = raw['track_artist']
            artist_entries_for_track = track_artist[track_artist['track_uri'] == track_uri]
            out = pd.merge(artist_entries_for_track, out, on="artist_uri")\
                .sort_values(by="artist_index", ascending=True)\
                .drop(columns=["artist_index", "track_uri"])

        if album_uri is not None:
            album_artist = raw['album_artist']
            uris = set(album_artist[album_artist['album_uri'] == album_uri]['artist_uri'])
            out = out[out['artist_uri'].isin(uris)]

        return out
    

    def mb_artist(self, mbid: str) -> pd.Series:
        return self.mb_artists(mbids = {mbid}).iloc[0]
    

    def mb_artists(self, mbids: typing.Iterable[str] = None, with_page: bool = False):
        out = RawData()['mb_artists']
        out['producer_has_page'] = out['artist_mbid'].isin(self.producers_with_page())

        if mbids is not None:
            out = out[out['artist_mbid'].isin(mbids)]

        if with_page:
            out = out[out['producer_has_page']]

        return out
    

    def producers_with_page(self):
        if self._producers_with_page is None:
            credits = RawData()['mb_recording_credits']
            credits = credits[credits['credit_type'].isin(producer_credit_types)]
            grouped = credits.groupby('artist_mbid').agg({'recording_mbid': 'count'}).reset_index()
            filtered = grouped[grouped['recording_mbid'] > 10]
            mbids = filtered['artist_mbid']
            self._producers_with_page = mbids
        return self._producers_with_page


    def related_artists(self, artist_uri: str) -> pd.DataFrame:
        raw = RawData()
        artist_join = raw['sp_artist_mb_artist']
        if artist_uri not in set(artist_join['spotify_artist_uri']):
            return None

        own_mbid = artist_join[artist_join['spotify_artist_uri'] == artist_uri].iloc[0]['artist_mbid']
        if own_mbid is None:
            return None

        relationships = raw['mb_artist_relationships']
        forward_relationships = relationships[relationships['artist_mbid'] == own_mbid]
        backward_relationships = relationships[relationships['other_mbid'] == own_mbid]

        if len(forward_relationships) == 0 and len(backward_relationships) == 0:
            return None

        forward_relationships = pd.merge(forward_relationships, artist_join, how="left", left_on='other_mbid', right_on='artist_mbid')
        backward_relationships = pd.merge(backward_relationships, artist_join, how="left", on='artist_mbid')

        related_artist_uris = set(forward_relationships['spotify_artist_uri'].dropna())\
                       .union(set(backward_relationships['spotify_artist_uri'].dropna()))
        related_artists = self.artists(related_artist_uris)

        forward_relationships = pd.merge(forward_relationships, related_artists, how="left", left_on="spotify_artist_uri", right_on="artist_uri")
        backward_relationships = pd.merge(backward_relationships, related_artists, how="left", left_on="spotify_artist_uri", right_on="artist_uri")

        mb_artists = raw['mb_artists']
        forward_relationships = pd.merge(forward_relationships, mb_artists, left_on="other_mbid", right_on="artist_mbid")
        backward_relationships = pd.merge(backward_relationships, mb_artists, on="artist_mbid")

        forward_relationships['relationship_direction'] = 'forward'
        backward_relationships['relationship_direction'] = 'backward'

        return pd.concat([forward_relationships, backward_relationships]).sort_values(by=['relationship_type', 'relationship_direction', 'artist_sort_name'])


    def group_members(self, artist_uri: str) -> pd.DataFrame:
        related = self.related_artists(artist_uri)
        if related is None:
            return None
        
        members = related[(related['relationship_type'] == 'member of band') & (related['relationship_direction'] == 'backward')]

        if len(members) == 0:
            return None

        return members[[col for col in members.columns if col.startswith('artist_')]]


    def top_artists(self, current: bool = None, top: int = None, term: str = None, artist_uris: typing.Iterable[str] = None) -> pd.DataFrame:
        out = RawData()['top_artists']

        if current:
            most_recent_date = out['as_of_date'].iloc[0]
            out = out[out['as_of_date'] == most_recent_date]
            out = out.drop(columns=['as_of_date'])

        if term is not None:
            out = out[out['term'] == term]

        if top is not None:
            out = out[out['index'] <= top]

        if artist_uris is not None:
            out = out[out['artist_uri'].isin(artist_uris)]

        return out.copy()
    

    def track_counts_by_artist(self, track_uris: typing.Iterable[str] = None) -> pd.DataFrame:
        if self._track_artist is None:
            track_artist = pd.merge(self.tracks(), RawData()['track_artist'], on='track_uri')
            track_artist = pd.merge(track_artist, self.artists(), on='artist_uri')
            self._track_artist = track_artist

        return self._track_artist[self._track_artist['track_uri'].isin(track_uris)]\
            .groupby("artist_uri")\
            .agg({"track_uri": "count", "track_liked": "sum", "artist_name": first, "artist_image_url": first})\
            .reset_index()
    

    def labels(self, track_uris: typing.Iterable[str] = None, with_page: bool = None) -> pd.DataFrame:
        if self._album_label is None:
            self._album_label = standardize_record_labels(self.albums(), self.tracks())

        out = pd.merge(self.tracks(uris=track_uris), self._album_label, on="album_uri")\
            .groupby("album_standardized_label")\
            .agg({"track_uri": "count", "track_liked": "sum", "label_has_page": first})\
            .reset_index()\
            .rename(columns={"track_uri": "label_track_count", "track_liked": "label_track_liked_count"})
        
        if with_page is not None:
            out = out[out['label_has_page'] == with_page]

        return out
    

    def album_label(self):
        if self._album_label is None:
            self._album_label = standardize_record_labels(self.albums(), self.tracks())

        return self._album_label
    

    def genres(self, with_page: bool = None) -> typing.Iterable[str]:
        if with_page:
            out = self.track_genre()
            out = out[out['genre_has_page'] == True]
            return out.groupby('genre').agg({'track_uri': "sum"}).reset_index()['genre']
        
        rd = RawData()
        return rd['artist_genre']['genre'].unique()
        

    def track_genre(self, track_uris: typing.Iterable[str] = None) -> pd.DataFrame:
        if self._track_genre is None:
            self.__initialize_genre_join_tables()

        if track_uris is not None:
            return self._track_genre[self._track_genre['track_uri'].isin(track_uris)]

        return self._track_genre
    

    def artist_genre(self) -> pd.DataFrame:
        if self._artist_genre is None:
            self.__initialize_genre_join_tables()

        return self._artist_genre


    def __initialize_genre_join_tables(self):
        if self._artist_genre is not None and self._track_genre is not None:
            return
        
        rd = RawData()
        tracks = rd['tracks'].copy()
        artist_genre = rd['artist_genre'].copy()
        track_artist = rd['track_artist']
        liked_tracks = rd['liked_tracks']

        liked_track_uris = set(liked_tracks["track_uri"])
        tracks["track_liked"] = tracks["track_uri"].isin(liked_track_uris)
        track_primary_artist = pd.merge(tracks, track_artist[track_artist["artist_index"] == 0], on="track_uri")
        track_genre = pd.merge(track_primary_artist, artist_genre, on="artist_uri")
        track_genre.drop(columns=["artist_uri"], inplace=True)

        genre_artist_counts = artist_genre.groupby('genre').agg({'artist_uri': 'count'}).reset_index()
        genre_track_counts = track_genre.groupby("genre").agg({"track_uri": "count", "track_liked": "sum"}).reset_index()
        genre_counts = pd.merge(genre_track_counts, genre_artist_counts, on="genre")
        genres_with_page = set(genre_counts[
            (genre_counts["artist_uri"] > 1) \
            & (
                (genre_counts["track_uri"] >= 50) \
                | ((genre_counts["track_uri"] >= 30) & (genre_counts["track_liked"] > 0)) \
                | (genre_counts["track_liked"] > 20)
            )
        ]["genre"])

        track_genre['genre_has_page'] = track_genre['genre'].isin(genres_with_page)
        artist_genre['genre_has_page'] = artist_genre['genre'].isin(genres_with_page)

        self._track_genre = track_genre[['track_uri', 'genre', 'genre_has_page']]
        self._artist_genre = artist_genre[['artist_uri', 'genre', 'genre_has_page']]


    def __owned_track_uris(self):
        if self._owned_track_uris is None:
            raw = RawData()
            playlists = raw['playlists']
            playlist_track = raw['playlist_track']
            owned_playlists = playlists[playlists['playlist_owner'] != 'spotify']
            owned_tracks = pd.merge(owned_playlists, playlist_track, on='playlist_uri', how='inner')

            self._owned_track_uris = {u for u in owned_tracks['track_uri']}

        return self._owned_track_uris
    

    def __owned_album_uris(self):
        if self._owned_album_uris is None:
            tracks = RawData()['tracks']
            owned_tracks = tracks[tracks['track_uri'].isin(self.__owned_track_uris())]

            return {u for u in owned_tracks['album_uri']}
        
        return self._owned_album_uris



def add_primary_prefix(artists: pd.DataFrame):
    artists.columns = ['primary_' + col for col in artists.columns]
    return artists


def placement_score(index, term):
    multiplier = 1
    total = 50

    if term == 'on_repeat':
        multiplier = 3
        total = 30
    if term == 'medium_term':
        multiplier = 6
    if term == 'long_term':
        multiplier = 12

    return multiplier * (total + 1 - index)
    