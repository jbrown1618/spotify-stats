import os
from datetime import datetime
import pandas as pd

from utils.date import this_date, this_year
from utils.path import data_path, persistent_data_path


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
        source = data_sources.get(key, None)
        if source is None:
            raise RuntimeError(f'Invalid data source {key}')
        
        return source.data()

    
    def __setitem__(self, key: str, value: pd.DataFrame):
        source = data_sources.get(key, None)
        if source is None:
            raise RuntimeError(f'Invalid data source {key}')
        
        source.set_data(value)


class DataSource:
    def __init__(self, key: str, index: list[str], prefix: str = None, persistent: bool = False):
        self.key = key
        self.index = index
        self.prefix = prefix
        self.persistent = persistent

        self._value: pd.DataFrame = None

        data_sources[key] = self


    def data(self) -> pd.DataFrame:
        if self._value is not None:
            return self._value
        
        print(f'Loading {self.key} data')
        if self.persistent:
            df = self._merge_all_years()
        else:
            df = pd.read_csv(data_path(self.key))

        self._prefix_df(df)

        self._value = df
        return self._value
    

    def set_data(self, value: pd.DataFrame):
        print(f'Updating {self.key} data')
        value = value.sort_values(by=self.index)
        path = data_path(self.key)

        if self.persistent:
            value = self._merge_persistent_data_source(value)
            path = persistent_data_path(self.key, this_year())

        value.to_csv(path, index=False)
        self._prefix_df(value)
        self._value = value


    def _merge_all_years(self) -> pd.DataFrame:
        year = this_year()
        merged = None

        while True:
            df_path = persistent_data_path(self.key, year)
            if not os.path.isfile(df_path):
                return merged
            
            df_for_year = pd.read_csv(df_path)
            if merged is None:
                merged = df_for_year
            else:
                merged = pd.concat([merged, df_for_year], axis=0)

            year = str(int(year) - 1)
    

    def _merge_persistent_data_source(self, value: pd.DataFrame) -> pd.DataFrame:
        value['as_of_date'] = this_date()
        
        current_file = persistent_data_path(self.key, this_year())
        if not os.path.isfile(current_file):
            return value
        
        current_df = pd.read_csv(current_file)
        date_strings = [d for d in current_df['as_of_date'].unique()]
        date_strings.sort()

        latest_date_str = date_strings[-1]
        next_latest_date_str = date_strings[-2]

        # Replace the most recent day of data if it is fewer than three days away from the previous day
        days_diff = (datetime.strptime(latest_date_str, '%Y-%m-%d') - datetime.strptime(next_latest_date_str, '%Y-%m-%d')).days
        should_replace_latest = days_diff < 3 or this_date() == latest_date_str

        if should_replace_latest:
            current_df = current_df[current_df['as_of_date'] != latest_date_str]

        value = pd.concat([value, current_df], axis=0).reset_index(drop=True)

        return value


    def _prefix_df(self, df: pd.DataFrame):
        if self.prefix is None:
            return
        
        df.columns = [self._prefix_col(col) for col in df.columns]

    
    def _prefix_col(self, col: str):
        prefixes = {s.prefix for s in data_sources.values() if s.prefix is not None}

        for other_prefix in prefixes:
            if col.startswith(other_prefix):
                return col
            
        return self.prefix + col


data_sources: dict[str, DataSource] = {}

DataSource('playlists',      index=["uri"],       prefix="playlist_")
DataSource('tracks',         index=["uri"],       prefix="track_")
DataSource('albums',         index=["uri"],       prefix="album_")
DataSource('audio_features', index=["track_uri"], prefix="audio_")
DataSource('artists',        index=["uri"],       prefix="artist_")

DataSource('album_artist',   index=["artist_uri", "album_uri"])
DataSource('artist_genre',   index=["artist_uri", "genre"])
DataSource('liked_tracks',   index=["track_uri"])
DataSource('playlist_track', index=["playlist_uri", "track_uri"])
DataSource('track_artist',   index=["track_uri", "artist_uri"])

DataSource('top_artists',    index=["term", "index"], persistent=True)
DataSource('top_tracks',     index=["term", "index"], persistent=True)
