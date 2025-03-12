from datetime import datetime, timedelta
import pandas as pd
from data.query import query_text
from data.raw import get_connection
from jobs.queue import queue_job
from jobs.save_spotify_data import save_tracks_by_uri
from spotify.spotify_client import get_spotify_client

played_at_date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
max_listening_period_s = 7 * 24 * 60 * 60  # 7 days

def save_listening_data():
    sp = get_spotify_client()
    print("Fetching recent listening history...")
    recents = sp.current_user_recently_played(limit=50)

    plays_data = []
    for recent_play in recents['items']:
        track_uri = recent_play['track']['uri']
        played_at = recent_play['played_at']
        time = datetime.strptime(played_at, played_at_date_format).timestamp()
        plays_data.append({ "track_uri": track_uri, "time": time })
    plays = pd.DataFrame(plays_data)

    current_min, current_id, new_min, new_id = get_listening_period(plays['time'].min(), plays['time'].max())

    current_plays = plays[(plays['time'] >= current_min) & (plays['time'] < new_min)] \
                    if new_min is not None \
                    else plays[plays['time'] >= current_min]
    
    new_plays = plays[plays['time'] >= new_min] \
                if new_min is not None \
                else plays.head(0)

    should_re_rank = False

    if len(current_plays) > 0:
        current_play_counts = current_plays.groupby('track_uri')\
            .agg({"time": "count"})\
            .reset_index()\
            .rename(columns={"time": "stream_count"})
        
        update_play_counts(current_id, current_play_counts)
        should_re_rank = True
    
    if len(new_plays) > 0:
        new_play_counts = new_plays.groupby('track_uri')\
            .agg({"time": "count"})\
            .reset_index()\
            .rename(columns={"time": "stream_count"})
        update_play_counts(new_id, new_play_counts)
        should_re_rank = True
    
    if should_re_rank:
        queue_job("ensure_ranks", { "force": True })

    unsaved_uris = get_unsaved_track_uris()
    if len(unsaved_uris) > 0:
        save_tracks_by_uri(unsaved_uris)



def get_listening_period(min_time: float, max_time: float):
    """
    Returns:
    - The min time to consider for the current period
    - The ID of the current period
    - The min time to consider for the new period, if any
    - The ID of the new period, if any
    """
    month = datetime.fromtimestamp(max_time).month
    current = get_latest_listening_period()

    if current is None:
        # This case should not be hit often; it accounts for the case where
        # there are no listening periods in the database yet.
        create_listening_period(min_time, max_time)
        return min_time, get_latest_listening_period()[0], None, None

    current_id, current_from, current_to = current
    if month != current_to.month:
        # If we are in a new month, extend the current period to the end of
        # the month and create a new period starting at the beginning of the new month
        start_of_new_month = datetime.fromtimestamp(max_time).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_current_month = start_of_new_month - timedelta(seconds=1)
        
        update_listening_period(current_id, end_of_current_month.timestamp())
        create_listening_period(start_of_new_month.timestamp(), max_time)
        return current_to.timestamp(), current_id, start_of_new_month.timestamp(), get_latest_listening_period()[0]
    
    elif max_time - current_from.timestamp() > max_listening_period_s:
        # If updating the current listening period would make it longer
        # than the maximum, create a new listening period that starts
        # just after the current one ends
        new_period_start = current_to.timestamp() + 1
        create_listening_period(new_period_start, max_time)
        return new_period_start, get_latest_listening_period()[0], None, None
    
    else:
        # Otherwise, update the current listening period to extend to
        # the current time.
        update_listening_period(current_id, max_time)
        return current_to.timestamp() + 1, get_latest_listening_period()[0], None, None



def create_listening_period(from_time: float, to_time: float):
    print(f'Creating listening period from {from_time} to {to_time}')
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('insert_listening_period'), 
            {"ft": from_time, "tt": to_time}
        )
        conn.commit()


def update_listening_period(id, to_time: float):
    print(f'Updating the end of listening period {id} to {to_time}')
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_text('update_listening_period'), {"period_id": id, "tt": to_time})
        conn.commit()


def get_latest_listening_period():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_text('select_latest_listening_period'))
        return cursor.fetchone()


def update_play_counts(period_id: int, play_counts: pd.DataFrame):
    print('Updating play counts: ')
    print(play_counts)

    with get_connection() as conn:
        cursor = conn.cursor()
        for _, row in play_counts.iterrows():
            cursor.execute(
                query_text('update_stream_counts'), 
                {
                    "period_id": period_id,
                    "track_uri": row["track_uri"],
                    "stream_count": row["stream_count"]
                }
            )
        conn.commit()


def get_unsaved_track_uris():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_text('select_tracks_without_streams'))
        return [row[0] for row in cursor.fetchall()]


if __name__ == '__main__':
    save_listening_data()
