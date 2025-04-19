import typing
import pandas as pd
import sqlalchemy

from data.query import query_text
from data.raw import RawData, get_engine
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
        
        self._owned_albums = None
        self._owned_tracks = None

        self._album_label = None
        self._album_artist = None
        self._playlist_track = None
        self._track_artist = None
        self._artist_genre = None
        self._track_genre = None
        self._genres_with_page = None
        self._track_artist = None
        self._track_credits = None
        self._producers_with_page = None
        self._owned_track_uris = None
        self._owned_album_uris = None

        self._initialized = True


    def track(self, uri: str):
        return self.tracks(uris={uri}).iloc[0]


    def tracks(self, 
               uris: typing.Iterable[str] = None, 
               liked: bool = None, 
               labels: typing.Iterable[str] = None, 
               genres: typing.Iterable[str] = None, 
               producers: typing.Iterable[str] = None,
               years: typing.Iterable[str] = None, 
               album_uris: typing.Iterable[str] = None, 
               playlist_uris: typing.Iterable[str] = None,
               artist_uris: typing.Iterable[str] = None) -> pd.DataFrame:
        with get_engine().begin() as conn:
            return pd.read_sql_query(sqlalchemy.text(query_text('select_tracks')), conn, params={
                "filter_tracks": uris is not None,
                "track_uris": tuple(['EMPTY']) if uris is None or len(uris) == 0 else tuple(uris),
                "liked": bool(liked),
                "filter_playlists": playlist_uris is not None,
                "playlist_uris": tuple(['EMPTY']) if playlist_uris is None or len(playlist_uris) == 0 else tuple(playlist_uris),
                "filter_artists": artist_uris is not None,
                "artist_uris": tuple(['EMPTY']) if artist_uris is None or len(artist_uris) == 0 else tuple(artist_uris),
                "filter_albums": album_uris is not None,
                "album_uris": tuple(['EMPTY']) if album_uris is None or len(album_uris) == 0 else tuple(album_uris),
                "filter_labels": labels is not None,
                "labels": tuple(['EMPTY']) if labels is None or len(labels) == 0 else tuple(labels),
                "filter_genres": genres is not None,
                "genres": tuple(['EMPTY']) if genres is None or len(genres) == 0 else tuple(genres),
                "filter_producers": producers is not None,
                "producers": tuple(['EMPTY']) if producers is None or len(producers) == 0 else tuple(producers),
                "filter_years": years is not None,
                "years": tuple([0]) if years is None or len(years) == 0 else tuple(years)
            })


    def playlists(self, track_uris: str = None) -> pd.DataFrame:
        with get_engine().begin() as conn:
            return pd.read_sql_query(sqlalchemy.text(query_text('select_playlists')), conn, params={
                "filter_tracks": track_uris is not None,
                "track_uris": tuple(['EMPTY']) if track_uris is None or len(track_uris) == 0 else tuple(track_uris)
            })


    def albums(self, track_uris: typing.Iterable[str] = None) -> pd.DataFrame:
        with get_engine().begin() as conn:
            albums = pd.read_sql_query(sqlalchemy.text(query_text('select_albums')), conn, params={
                "filter_tracks": track_uris is not None,
                "track_uris": tuple(['EMPTY']) if track_uris is None or len(track_uris) == 0 else tuple(track_uris)
            })
            return albums


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
    

    def artist(self, uri: str = None, mbid: str = None) -> pd.Series:
        if uri is not None:
            return self.artists(uris={uri}).iloc[0]
        
        if mbid is not None:
            return self.artists(mbids={mbid}).iloc[0]
        
        return None
    

    def artists(self, 
                uris: typing.Iterable[str] = None, 
                track_uris: typing.Iterable[str] = None, 
                mbids: typing.Iterable[str] = None):
        with get_engine().begin() as conn:
            return pd.read_sql_query(sqlalchemy.text(query_text('select_artists')), conn, params={
                "filter_tracks": track_uris is not None,
                "track_uris": tuple(['EMPTY']) if track_uris is None or len(track_uris) == 0 else tuple(track_uris),
                "filter_artists": uris is not None,
                "artist_uris": tuple(['EMPTY']) if uris is None or len(uris) == 0 else tuple(uris),
                "filter_mbids": mbids is not None,
                "mbids": tuple(['EMPTY']) if mbids is None or len(mbids) == 0 else tuple(mbids),
            })


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


    def producers(self, track_uris: typing.Iterable[str] = None) -> pd.DataFrame:
        with get_engine().begin() as conn:
            producers = pd.read_sql_query(sqlalchemy.text(query_text('select_producers')), conn, params={
                "filter_tracks": track_uris is not None,
                "track_uris": tuple(['EMPTY']) if track_uris is None or len(track_uris) == 0 else tuple(track_uris)
            })
            producers.drop_duplicates(subset=['producer_mbid'], keep='first', inplace=True)
            return producers


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
            .agg({"track_uri": "count", "track_liked": "sum", "artist_name": first, "artist_image_url": first, "artist_rank": first})\
            .reset_index()
    

    def labels(self, album_uris: typing.Iterable[str] = None) -> pd.DataFrame:
        with get_engine().begin() as conn:
            return pd.read_sql_query(sqlalchemy.text(query_text('select_labels')), conn, params={
                "filter_albums": album_uris is not None,
                "album_uris": tuple(['EMPTY']) if album_uris is None or len(album_uris) == 0 else tuple(album_uris)
            })['standardized_label'].to_list()
    

    def genres(self, artist_uris: typing.Iterable[str]) -> typing.Iterable[str]:
        with get_engine().begin() as conn:
            return pd.read_sql_query(sqlalchemy.text(query_text('select_genres')), conn, params={
                "filter_artists": artist_uris is not None,
                "artist_uris": tuple(['EMPTY']) if artist_uris is None or len(artist_uris) == 0 else tuple(artist_uris)
            })['genre'].to_list()


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


def add_primary_prefix(artists: pd.DataFrame):
    artists.columns = ['primary_' + col for col in artists.columns]
    return artists
