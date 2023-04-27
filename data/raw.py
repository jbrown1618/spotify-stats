import pandas as pd

from utils.path import data_path


valid_data_sources = {
    'album_artist',
    'albums',
    'artist_genre',
    'artists',
    'audio_features',
    'liked_tracks',
    'playlist_track',
    'playlists',
    'top_artists',
    'top_tracks',
    'track_artist',
    'tracks'
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

    
    def __getitem__(self, key: str) -> pd.DataFrame:
        if key not in valid_data_sources:
            raise RuntimeError(f'Invalid data source {key}')

        if key not in self._data:
            df = pd.read_csv(data_path(key))
            self._prefix_df(key, df)

            self._data[key] = df

        return self._data[key]
    
    def __setitem__(self, key: str, value: pd.DataFrame):
        if key not in valid_data_sources:
            raise RuntimeError(f'Invalid data source {key}')
        
        value.to_csv(data_path(key), index=False)
        self._prefix_df(key, value)
        self._data[key] = value


    def _prefix_df(self, key, df):
        prefix = df_prefixes.get(key, None)
        if prefix is None:
            return
        
        df.columns = [self._prefix_col(col, prefix) for col in df.columns]

    
    def _prefix_col(self, col: str, prefix):
        prefixes = set(df_prefixes.values())
        for other_prefix in prefixes:
            if col.startswith(other_prefix):
                return col
        return prefix + col
