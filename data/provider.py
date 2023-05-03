import typing
import pandas as pd

from data.raw import RawData
from utils.album import short_album_name
from utils.date import release_year
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

        self._initialized = True

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


    def tracks(self, uris: typing.Iterable[str] = None, liked: bool = None, label: str = None, genre: str = None) -> pd.DataFrame:
        if self._tracks is None:
            raw = RawData()
            tracks = pd.merge(raw["tracks"], raw["audio_features"], on="track_uri")
            tracks = pd.merge(tracks, self.albums(), on="album_uri")

            liked_track_uris = set(raw["liked_tracks"]["track_uri"])
            tracks["track_liked"] = tracks["track_uri"].isin(liked_track_uris)

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

        return out
    

    def labels(self, track_uris: typing.Iterable[str] = None, with_page: bool = None):
        if self._album_label is None:
            self._album_label = standardize_record_labels(self.albums(), self.tracks())

        out = pd.merge(self.tracks(uris=track_uris), self._album_label, on="album_uri")\
            .groupby("album_standardized_label")\
            .agg({"track_uri": "count", "track_liked": "sum", "label_has_page": first})\
            .reset_index()\
            .rename(columns={"track_uri": "track_count", "track_liked": "track_liked_count"})
        
        if with_page is not None:
            out = out[out['label_has_page'] == with_page]

        return out
    

    def genres(self, with_page: bool = None) -> typing.Iterable[str]:
        if with_page:
            out = self.track_genre()
            out = out[out['genre_has_page'] == True]
            return out.groupby('genre').agg({'track_uri': "sum"}).reset_index()['genre']
        
        rd = RawData()
        return rd['artist_genre']['genre'].unique()
        

    def track_genre(self, track_uris: typing.Iterable[str] = None):
        if self._track_genre is None:
            self.__initialize_genre_join_tables()

        if track_uris is not None:
            return self._track_genre[self._track_genre['track_uri'].isin(track_uris)]

        return self._track_genre
    

    def artist_genre(self):
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