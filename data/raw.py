import os
from datetime import datetime
import pandas as pd
import psycopg2
import sqlalchemy
import sqlalchemy.dialects
import sqlalchemy.dialects.postgresql

from utils.date import this_date, this_year
import utils.path as p
from utils.settings import postgres_host, postgres_password, postgres_port, postgres_url, postgres_user

def get_engine():
    url = postgres_url()
    if url is not None:
        if url.startswith("postgres") and not url.startswith("postgresql+psycopg2"):
            url = "postgresql+psycopg2" + url[len("postgres"):]
        return sqlalchemy.create_engine(url)
    else:
        return sqlalchemy.create_engine(f"postgresql+psycopg2://{postgres_user()}:{postgres_password()}@{postgres_host()}/spotifystats")


def get_connection():
    url = postgres_url()
    if url is not None:
        return psycopg2.connect(url, sslmode="require")
    else:
        return psycopg2.connect(database="spotifystats",
                                host=postgres_host(),
                                user=postgres_user(),
                                password=postgres_password(),
                                port=postgres_port())
    
update_batch_size = 500

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
    def __init__(self, source: str, key: str, index: list[str], prefix: str = None, persistent: bool = False, merge_on_set: bool = False, delete_before_set: bool = False):
        self.source = source
        self.key = key
        self.index = index
        self.prefix = prefix
        self.persistent = persistent
        self.merge_on_set = merge_on_set
        self.delete_before_set = delete_before_set

        self._value: pd.DataFrame = None

        data_sources[key] = self


    def data(self) -> pd.DataFrame:
        if self._value is not None:
            return self._value
        
        print(f'Loading {self.key} data')
        with get_engine().begin() as conn:
            df = pd.read_sql_table(self._table_name(), conn)

        self._prefix_df(df)

        self._value = df
        return self._value
    

    def set_data(self, value: pd.DataFrame):
        if value is None:
            return
            
        print(f'Updating {self.key} data')
        
        conn = get_connection()
        cursor = conn.cursor()

        if self.delete_before_set:
            cursor.execute(f'TRUNCATE {self._table_name()};')

        if self.persistent and 'as_of_date' not in value.columns:
            value['as_of_date'] = this_date()

        placeholders = [f"%({col})s" for col in value.columns]

        conflict_keys = self.index + ["as_of_date"] if self.persistent else self.index

        non_conflict_keys = [col for col in value.columns if col not in conflict_keys]
        non_conflict_placeholders = [f"%({col})s" for col in non_conflict_keys]

        conflict_operation = f"""
            ON CONFLICT ({", ".join(conflict_keys)}) DO UPDATE
            SET ({", ".join(non_conflict_keys)}) = (SELECT {", ".join(non_conflict_placeholders)});
        """ if len(non_conflict_keys) > 0 else """
            ON CONFLICT DO NOTHING
        """

        insert_statement = f"""
            INSERT INTO {self._table_name()}
            ({", ".join(value.columns)})
            VALUES
            ({", ".join(placeholders)})
            {conflict_operation}
        """

        for i, row in value.iterrows():
            value_map = {
                col: row[col]
                for col in value.columns
            }

            cursor.execute(insert_statement, value_map)

            if i > 0 and i % update_batch_size == 0:
                # Prevent timeouts by getting a new connection every so often
                conn.commit()
                conn = get_connection()
                cursor = conn.cursor()

        conn.commit()

        self.data()
        return


    def _table_name(self) -> str:
        return self.key[0:-1] if self.key.endswith("s") else self.key

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
DataSource('spotify', 'artists',        index=["uri"],       prefix="artist_")

DataSource('spotify', 'album_artist',   index=["artist_uri", "album_uri"])
DataSource('spotify', 'artist_genre',   index=["artist_uri", "genre"])
DataSource('spotify', 'liked_tracks',   index=["track_uri"], delete_before_set=True)
DataSource('spotify', 'playlist_track', index=["playlist_uri", "track_uri"], delete_before_set=True)
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
