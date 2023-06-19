import os
from datetime import datetime
import pandas as pd

from utils.path import data_path, persistent_data_path, persistent_data_sources


today = datetime.today()

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
            cls._instance._initialized = False

        return cls._instance
    

    def __init__(self):
        if self._initialized:
            return
        
        self._data = {}
        self._initialized = True

    
    def __getitem__(self, key: str) -> pd.DataFrame:
        if key not in valid_data_sources:
            raise RuntimeError(f'Invalid data source {key}')

        if key in self._data:
            return self._data[key]
        
        if key in persistent_data_sources:
            df = self._merge_all_years(key)
        else:
            df = pd.read_csv(data_path(key))

        self._prefix_df(key, df)

        self._data[key] = df
        return self._data[key]
    

    def _merge_all_years(self, key: str) -> pd.DataFrame:
        year = today.strftime('%Y')
        merged = None

        while True:
            df_path = persistent_data_path(key, year)
            if not os.path.isfile(df_path):
                return merged
            
            df_for_year = pd.read_csv(df_path)
            if merged is None:
                merged = df_for_year
            else:
                merged = pd.concat([merged, df_for_year], axis=0)

            year = str(int(year) - 1)

    
    def __setitem__(self, key: str, value: pd.DataFrame):
        if key not in valid_data_sources:
            raise RuntimeError(f'Invalid data source {key}')
        
        path = data_path(key)

        if key in persistent_data_sources:
            value = self._merge_persistent_data_source(key, value)
            path = persistent_data_path(key, today.strftime('%Y'))

        value.to_csv(path, index=False)
        self._prefix_df(key, value)
        self._data[key] = value


    def _merge_persistent_data_source(self, key: str, value: pd.DataFrame) -> pd.DataFrame:
        this_year = today.strftime('%Y')
        this_day = today.strftime('%Y-%m-%d')
        value['as_of_date'] = this_day
        
        current_file = persistent_data_path(key, this_year)
        if not os.path.isfile(current_file):
            return value
        
        current_df = pd.read_csv(current_file)
        date_strings = [d for d in current_df['as_of_date'].unique()]
        date_strings.sort()

        latest_date_str = date_strings[-1]
        next_latest_date_str = date_strings[-2]

        should_replace_latest = (datetime.strptime(latest_date_str, '%Y-%m-%d') - datetime.strptime(next_latest_date_str, '%Y-%m-%d')).days < 3

        if should_replace_latest:
            # If the most recent day is within 3 days
            current_df = current_df[current_df['as_of_date'] != latest_date_str]

        value = pd.concat([value, current_df], axis=0)


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
