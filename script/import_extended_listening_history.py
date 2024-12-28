import sys
import json
import typing
from datetime import datetime, timedelta

import pandas as pd

from data.raw import get_connection
from jobs.repair_orphan_tracks import repair_orphan_tracks
from jobs.save_listening_data import create_listening_period, update_play_counts
from jobs.save_spotify_data import save_tracks_by_uri
from utils.ranking import ensure_ranks

"""
This script imports extended listening history from a Spotify data request.

Args:
- min_date: the minimum date for which we should import data
- max_date: the maximum date for which we should import data
- [filenames]: the file names of all the json files from the data request
Usage:

```
python -m script.import_extended_listening_history '2020-07-15' '2024-12-18' path/to/Streaming_History_Audio_2023-2024_1.json path/to/Streaming_History_Audio_2015-2023_0.json
```
"""

def import_extended_listening_history(min_date, max_date, filenames: typing.Iterable[str]):
    history_df = None
    for filename in filenames:
        with open(filename) as f:
            arr = json.loads(f.read())
            df = pd.DataFrame(arr)
            history_df = df if history_df is None else pd.concat([history_df, df])

    history_df = history_df[history_df['spotify_track_uri'].notna()]
    history_df['time'] = history_df['ts'].apply(to_ts)
    history_df = history_df[(history_df['time'] > min_date) & (history_df['time'] < max_date)]
    history_df = history_df.rename(columns={'spotify_track_uri': 'track_uri'})

    import_history_df(history_df[['time', 'track_uri']])


played_at_date_format = "%Y-%m-%dT%H:%M:%SZ"
def to_ts(date_str: str):
    return datetime.strptime(date_str, played_at_date_format).timestamp()


def import_history_df(df: pd.DataFrame):
    for from_ts, to_ts in make_periods(df['time'].min(), df['time'].max()):
        period_history = df[(df['time'] >= from_ts) & (df['time'] < to_ts)]

        stream_counts = period_history.groupby('track_uri')\
            .agg({"time": "count"})\
            .reset_index()\
            .rename(columns={"time": "stream_count"})
        
        create_listening_period(from_ts, to_ts)
        period_id = get_listening_period_id(from_ts)
        update_play_counts(period_id, stream_counts)


def make_periods(min_time: float, max_time: float):
    max_dt = datetime.fromtimestamp(max_time)

    periods = []

    done = False
    start = datetime.fromtimestamp(min_time)
    while not done:
        end = start + timedelta(days=7)
        if end.month != start.month:
            end = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)

        if end >= max_dt:
            end = max_dt
            done = True
        
        periods.append((start.timestamp(), end.timestamp()))
        start = end + timedelta(seconds=1)

    return periods


def import_missing_tracks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT track_uri
        FROM listening_history h
        LEFT JOIN track t ON t.uri = h.track_uri
        WHERE t.name IS NULL
    """)
    missing_uris = [row[0] for row in cursor.fetchall()]
    save_tracks_by_uri(missing_uris)


def get_listening_period_id(from_time: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id
        FROM listening_period
        WHERE from_time = TO_TIMESTAMP(%(ft)s)
    """, {"ft": from_time})
    return cursor.fetchone()[0]


if __name__ == '__main__':
    # min_date = sys.argv[1]
    # max_date = sys.argv[2]
    # filenames = sys.argv[3:]
    # import_extended_listening_history(datetime.strptime(min_date, "%Y-%m-%d").timestamp(), datetime.strptime(max_date, "%Y-%m-%d").timestamp(), filenames)
    # import_missing_tracks()
    # repair_orphan_tracks()
    ensure_ranks()