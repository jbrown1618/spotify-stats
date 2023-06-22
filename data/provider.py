import typing
import pandas as pd

from data.raw import RawData
from utils.album import short_album_name
from utils.date import release_year
from utils.machine_learning import prepare_ml_data
from utils.record_label import standardize_record_labels
from utils.util import first

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
        self._playlists = None
        self._tracks = None

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


    def albums(self, uris: typing.Iterable[str] = None) -> pd.DataFrame:
        if self._albums is None:
            raw = RawData()
            albums = raw["albums"].copy()
            albums['album_release_year'] = albums['album_release_date'].apply(release_year)
            albums['album_short_name'] = albums['album_name'].apply(short_album_name)
            self._albums = albums
        
        out = self._albums

        if uris is not None:
            out = out[out["album_uri"].isin(uris)]
        
        return out
        

    def tracks(self, 
               uris: typing.Iterable[str] = None, 
               liked: bool = None, 
               label: str = None, 
               genre: str = None, 
               album_uri: str = None, 
               playlist_uri: str = None,
               artist_uri: str = None) -> pd.DataFrame:
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

            tracks = pd.merge(tracks, track_primary_artist, on="track_uri")
            tracks = pd.merge(tracks, artists, on="primary_artist_uri")

            self._tracks = tracks

        out = self._tracks

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
    

    def top_tracks(self, current: bool = None, top: int = None, term: str = None, track_uris: typing.Iterable[str] = None):
        out = RawData()['top_tracks']

        if current:
            most_recent_date = out['as_of_date'].iloc[0]
            out = out[out['as_of_date'] == most_recent_date]
            out = out.drop(columns=['as_of_date'])

        if term is not None:
            out = out[out['term'] == term]

        if top is not None:
            out = out[out['index'] <= top]

        if track_uris is not None:
            out = out[out['track_uri'].isin(track_uris)]

        return out
    
    def top_artists(self, current: bool = None, top: int = None, term: str = None, artist_uris: typing.Iterable[str] = None):
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
    

    def artist(self, uri: str) -> pd.Series:
        return self.artists(uris={uri}).iloc[0]
    

    def artists(self, 
                uris: typing.Iterable[str] = None, 
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
            artist_track_counts.fillna(0, inplace=True)
            
            artist_track_counts["artist_has_page"] = (artist_track_counts["artist_track_count"] >= 10) & (artist_track_counts["artist_liked_track_count"] > 0)

            self._artists = pd.merge(raw['artists'], artist_track_counts, on="artist_uri")

        out = self._artists

        if uris is not None:
            out = out[out['artist_uri'].isin(uris)]

        if with_page is not None:
            out = out[out['artist_has_page'] == with_page]

        if track_uri is not None:
            track_artist = raw['track_artist']
            uris = track_artist[track_artist['track_uri'] == track_uri]['artist_uri']
            out = out[out['artist_uri'].isin(uris)]

        if album_uri is not None:
            album_artist = raw['album_artist']
            uris = set(album_artist[album_artist['album_uri'] == album_uri]['artist_uri'])
            out = out[out['artist_uri'].isin(uris)]

        return out
    

    def top_artists(self, current: bool = None, top: int = None, term: str = None, artist_uris: typing.Iterable[str] = None):
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

        return out
    

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

        genre_track_counts = track_genre.groupby("genre").agg({"track_uri": "count", "track_liked": "sum"}).reset_index()
        genres_with_page = set(genre_track_counts[(genre_track_counts["track_uri"] >= 40) & (genre_track_counts["track_liked"] > 0)]["genre"])

        track_genre['genre_has_page'] = track_genre['genre'].isin(genres_with_page)
        artist_genre['genre_has_page'] = artist_genre['genre'].isin(genres_with_page)

        self._track_genre = track_genre[['track_uri', 'genre', 'genre_has_page']]
        self._artist_genre = artist_genre[['artist_uri', 'genre', 'genre_has_page']]


def add_primary_prefix(artists: pd.DataFrame):
    artists.columns = ['primary_' + col for col in artists.columns]
    return artists