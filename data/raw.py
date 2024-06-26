import os
from datetime import datetime
import pandas as pd

from utils.date import this_date, this_year
import utils.path as p


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
    def __init__(self, source: str, key: str, index: list[str], prefix: str = None, persistent: bool = False, merge_on_set: bool = False):
        self.source = source
        self.key = key
        self.index = index
        self.prefix = prefix
        self.persistent = persistent
        self.merge_on_set = merge_on_set

        self._value: pd.DataFrame = None

        data_sources[key] = self


    def data(self) -> pd.DataFrame:
        if self._value is not None:
            return self._value
        
        print(f'Loading {self.key} data')
        if self.persistent:
            df = self._merge_all_years()
        else:
            df = pd.read_csv(p.data_path(self.source, self.key))

        self._prefix_df(df)

        self._value = df
        return self._value
    

    def set_data(self, value: pd.DataFrame):
        path = p.data_path(self.source, self.key)

        if value is None:
            if self.persistent:
                raise ValueError("Cannot delete persistent data source")
            
            if not os.path.isfile(path):
                # Nothing to do
                return
            
            print(f'Deleting {self.key} data')
            existing = pd.read_csv(path)
            empty = pd.DataFrame(columns=existing.columns)

            empty.to_csv(path, index=False)
            self._prefix_df(value)
            self._value = value
            return

            
        print(f'Updating {self.key} data')
        value = value.sort_values(by=self.index)

        if self.persistent and 'as_of_date' not in value.columns:
            value = self._merge_into_current_year_data_source(value)
            path = p.persistent_data_path(self.source, self.key, this_year())

        if self.persistent and 'as_of_date' in value.columns:
            full_existing = self._merge_all_years()
            value = pd.concat([value, full_existing])
            value = value.drop_duplicates(subset=[c for c in self.index] + ['as_of_date'], keep="first")
            distinct_years = value['as_of_date'].str.slice(0,4).unique()
            for year in distinct_years:
                path = p.persistent_data_path(self.source, self.key, year)
                data = value[value['as_of_date'].str.startswith(year)]
                data.to_csv(path, index=False)

            self._prefix_df(value)
            self._value = value.reset_index(drop=True)
            return

        if self.merge_on_set and os.path.isfile(path):
            existing = pd.read_csv(path)            
            value = pd.concat([existing, value])
            value = value.drop_duplicates(subset=self.index, keep="last")
            value = value.sort_values(by=self.index)

        value.to_csv(path, index=False)

        if self.persistent:
            value = self._merge_all_years()

        self._prefix_df(value)

        self._value = value


    def _merge_all_years(self) -> pd.DataFrame:
        year = this_year()
        merged = None

        while True:
            df_path = p.persistent_data_path(self.source, self.key, year)
            if not os.path.isfile(df_path):
                return merged
            
            df_for_year = pd.read_csv(df_path)
            if merged is None:
                merged = df_for_year
            else:
                merged = pd.concat([merged, df_for_year], axis=0).reset_index(drop=True)

            year = str(int(year) - 1)
    

    def _merge_into_current_year_data_source(self, value: pd.DataFrame) -> pd.DataFrame:
        value['as_of_date'] = this_date()
        
        current_file = p.persistent_data_path(self.source, self.key, this_year())
        if not os.path.isfile(current_file):
            return value
        
        current_df = pd.read_csv(current_file)
        date_strings = [d for d in current_df['as_of_date'].unique()]
        date_strings.sort()

        latest_date_str = date_strings[-1]
        should_replace_latest = this_date() == latest_date_str

        if len(date_strings) > 1 and not should_replace_latest:
            next_latest_date_str = date_strings[-2]

            # Replace the most recent day of data if it is fewer than three days away from the previous day
            days_diff = (datetime.strptime(latest_date_str, '%Y-%m-%d') - datetime.strptime(next_latest_date_str, '%Y-%m-%d')).days
            should_replace_latest = days_diff < 3

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

DataSource('spotify', 'playlists',      index=["uri"],       prefix="playlist_")
DataSource('spotify', 'tracks',         index=["uri"],       prefix="track_")
DataSource('spotify', 'albums',         index=["uri"],       prefix="album_")
DataSource('spotify', 'audio_features', index=["track_uri"], prefix="audio_")
DataSource('spotify', 'artists',        index=["uri"],       prefix="artist_")

DataSource('spotify', 'album_artist',   index=["artist_uri", "album_uri"])
DataSource('spotify', 'artist_genre',   index=["artist_uri", "genre"])
DataSource('spotify', 'liked_tracks',   index=["track_uri"])
DataSource('spotify', 'playlist_track', index=["playlist_uri", "track_uri"])
DataSource('spotify', 'track_artist',   index=["track_uri", "artist_uri"])

DataSource('spotify', 'top_artists',    index=["term", "index"], persistent=True)
DataSource('spotify', 'top_tracks',     index=["term", "index"], persistent=True)

DataSource('musicbrainz', 'mb_recordings', index=['recording_mbid'], merge_on_set=True)
DataSource('musicbrainz', 'mb_artists', index=['artist_mbid'], merge_on_set=True)
DataSource('musicbrainz', 'mb_recording_credits', index=["recording_mbid", "artist_mbid", "credit_type"], merge_on_set=True)
DataSource('musicbrainz', 'mb_artist_relationships', index=["artist_mbid", "other_mbid", "relationship_type"], merge_on_set=True)
DataSource('musicbrainz', 'mb_tags', index=['mb_tag', 'artist_mbid'], merge_on_set=True)
DataSource('musicbrainz', 'mb_unfetchable_isrcs', index=["isrc"], merge_on_set=True)
DataSource('musicbrainz', 'mb_unmatchable_artists', index=["artist_uri"], merge_on_set=True)

DataSource('musicbrainz', 'sp_track_mb_recording', index=["spotify_track_uri", "recording_mbid"], merge_on_set=True)
DataSource('musicbrainz', 'sp_artist_mb_artist', index=["spotify_artist_uri", "artist_mbid"], merge_on_set=True)
