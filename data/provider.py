import typing
import pandas as pd

from data.raw import RawData
from utils.album import short_album_name
from utils.date import release_year

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


    def tracks(self, uris: typing.Iterable[str] = None, liked: bool = None) -> pd.DataFrame:
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
        
        return out