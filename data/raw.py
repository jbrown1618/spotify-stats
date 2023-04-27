import pandas as pd

from utils.path import data_path


valid_data_sources = {
    'album_artist',
    'albums',
    'artists',
    'audio_features',
    'liked_tracks',
    'playlist_track',
    'playlists',
    'track_artist',
    'tracks',
    'artist_genre',
    'top_tracks',
    'top_artists'
}

df_prefixes = {
    "albums": "album_",
    "tracks": "track_",
    "audio_features": "audio_",
    "playlists": "playlist_",
    "artists": "artist_"
}


class RawData:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RawData, cls).__new__(cls)

        return cls._instance
    

    def __init__(self):
        self._data = {}

    
    def __getitem__(self, key) -> pd.DataFrame:
        if key not in valid_data_sources:
            raise RuntimeError(f'Invalid data source {key}')

        if key not in self._data:
            df = pd.read_csv(data_path(key))
            prefix = df_prefixes.get(key, None)
            if prefix is not None:
                prefix_df(df, prefix, set(df_prefixes.values()))

            self._data[key] = df

        return self._data[key]
    

def prefix_df(df: pd.DataFrame, prefix: str, prefixes: list[str]):
    df.columns = [prefix_col(col, prefix, prefixes) for col in df.columns]


def prefix_col(col: str, prefix: str, prefixes: list[str]):
    for other_prefix in prefixes:
        if col.startswith(other_prefix):
            return col
    return prefix + col