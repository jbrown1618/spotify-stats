import os
from datetime import datetime
import pandas as pd

from utils.date import this_date, this_year, today
from utils.path import data_cache_stamp_path, data_path, persistent_data_path


class DataSource:
    short_cache = 30
    long_cache = 365

    def __init__(self, key: str, index: list[str], prefix: str = None, cache_days: int = None, persistent: bool = False, source_key: str = None):
        self.key = key
        self.index = index
        self.prefix = prefix
        self.cache_days = cache_days
        self.persistent = persistent
        self.source_key = source_key

        self._value: pd.DataFrame = None
        self._cached_uris: set[str] = None
        if not self.__is_cached() and not self.persistent and os.path.isfile(data_path(self.key)):
            print(f'Removing existing {self.key} data')
            os.remove(data_path(self.key))


    def data(self) -> pd.DataFrame:
        if self._value is not None:
            return self._value
        
        print(f'Loading {self.key} data')
        if self.persistent:
            df = self._merge_all_years()
        else:
            df = pd.read_csv(data_path(self.key))

        self.__prefix_df(df)

        self._value = df
        return self._value
    

    def set_data(self, value: pd.DataFrame):
        print(f'Updating {self.key} data')
        if len(value) == 0:
            return
        
        value = value.sort_values(by=self.index)
        self.__prefix_df(value)

        path = data_path(self.key)

        if self.persistent:
            value = self._merge_persistent_data_source(value)
            path = persistent_data_path(self.key, this_year())

        if self.__is_cached():
            cache_col = self.__prefix_col(self.index[0])
            existing = self.data()
            value = value[~value[cache_col].isin(self.cached_uris())]
            value = pd.concat([value, existing], axis=0)\
                .reset_index(drop=True)\
                .sort_values(by=cache_col)

        value.to_csv(path, index=False)
        self._value = value

        if self.__is_cacheable() and not self.__is_cached():
            with open(data_cache_stamp_path(self.key), 'w') as f:
                f.write(this_date())


    def cached_uris(self) -> set[str]:
        if not self.__is_cacheable():
            raise RuntimeError('Invalid data source for cached URIs')
        
        if self._cached_uris is not None:
            return self._cached_uris
        
        if not self.__is_cached():
            self._cached_uris = set()
            return self._cached_uris
        
        cache_col = self.__prefix_col(self.index[0])
        existing = self.data()

        self._cached_uris = set(existing[cache_col])
        return self._cached_uris


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
    

    def __is_cacheable(self):
        if self.cache_days is None:
            return False
        
        if self.cache_days == 0:
            return False
        
        if len(self.index) != 1:
            return False
        
        return True
    

    def __is_cached(self):
        if not self.__is_cacheable():
            return False
        
        cache_stamp_path = data_cache_stamp_path(self.key)
        if not os.path.isfile(cache_stamp_path):
            return False
        
        if not os.path.isfile(data_path(self.key)):
            return False
        
        with open(cache_stamp_path) as f:
            contents = f.read().strip()

        cache_datetime = datetime.strptime(contents, '%Y-%m-%d')
        days_since_cache = (cache_datetime - today()).days

        return days_since_cache <= self.cache_days


    def __prefix_df(self, df: pd.DataFrame):
        if self.prefix is None:
            return
        
        df.columns = [self.__prefix_col(col) for col in df.columns]

    
    def __prefix_col(self, col: str):
        prefixes = {"playlist_", "track_", "album_", "audio_", "artist_"}

        for other_prefix in prefixes:
            if col.startswith(other_prefix):
                return col
            
        return self.prefix + col


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
        
        self._data_sources: dict[str, DataSource] = {}

        self.__add_data_source(DataSource('playlists',      index=["uri"],       prefix="playlist_"))
        self.__add_data_source(DataSource('tracks',         index=["uri"],       prefix="track_"))
        self.__add_data_source(DataSource('albums',         index=["uri"],       prefix="album_",    cache_days=DataSource.short_cache))
        self.__add_data_source(DataSource('audio_features', index=["track_uri"], prefix="audio_",    cache_days=DataSource.long_cache))
        self.__add_data_source(DataSource('artists',        index=["uri"],       prefix="artist_",   cache_days=DataSource.short_cache))
        
        self.__add_data_source(DataSource('album_artist',   index=["artist_uri", "album_uri"]))
        self.__add_data_source(DataSource('artist_genre',   index=["artist_uri", "genre"]))
        self.__add_data_source(DataSource('liked_tracks',   index=["track_uri"]))
        self.__add_data_source(DataSource('playlist_track', index=["playlist_uri", "track_uri"]))
        self.__add_data_source(DataSource('track_artist',   index=["track_uri", "artist_uri"]))
        
        self.__add_data_source(DataSource('top_artists',    index=["term", "index"], persistent=True))
        self.__add_data_source(DataSource('top_tracks',     index=["term", "index"], persistent=True))
        
        self._initialized = True

    
    def __getitem__(self, key: str) -> pd.DataFrame:
        source = self._data_sources.get(key, None)
        if source is None:
            raise RuntimeError(f'Invalid data source {key}')
        
        return source.data()

    
    def __setitem__(self, key: str, value: pd.DataFrame):
        source = self._data_sources.get(key, None)
        if source is None:
            raise RuntimeError(f'Invalid data source {key}')
        
        source.set_data(value)


    def cached_uris(self, key: str) -> set[str]:
        source = self._data_sources.get(key, None)
        if source is None:
            raise RuntimeError(f'Invalid data source {key}')
        
        return source.cached_uris()


    def __add_data_source(self, ds: DataSource):
        self._data_sources[ds.key] = ds

