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

        return cls._instance
    

    def __init__(self):
        self._artists = None
        self._albums = None
        self._playlists = None
        self._tracks = None

        self._album_label = None
        self._album_artist = None
        self._playlist_track = None
        self._track_artist = None
        self._artist_genre = None


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


    def tracks(self, uris: typing.Iterable[str] = None, liked: bool = None, label: str = None) -> pd.DataFrame:
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
        
