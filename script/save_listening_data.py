from datetime import datetime
import pandas as pd
from data.raw import get_connection
from spotify.spotify_client import get_spotify_client

played_at_date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
max_listening_period_s = 5 * 24 * 60 * 60  # 5 days

def save_listening_data():
    sp = get_spotify_client()
    recents = sp.current_user_recently_played(limit=50)

    plays_data = []
    for recent_play in recents['items']:
        track_uri = recent_play['track']['uri']
        played_at = recent_play['played_at']
        time = datetime.strptime(played_at, played_at_date_format).timestamp()
        plays_data.append({ "track_uri": track_uri, "time": time })
    plays = pd.DataFrame(plays_data)

    current, min_time = get_listening_period(plays['time'].min(), plays['time'].max())
    period_id = current[0]

    plays = plays[plays['time'] >= min_time]

    play_counts = plays.groupby('track_uri')\
        .agg({"time": "count"})\
        .reset_index()\
        .rename(columns={"time": "stream_count"})

    update_play_counts(period_id, play_counts)


def get_listening_period(min_time: float, max_time: float):
    current = get_latest_listening_period()

    if current is None:
        # This case should not be hit often; it accounts for the case where
        # there are no listening periods in the database yet.
        create_listening_period(min_time, max_time)
        return get_latest_listening_period(), min_time

    current_id, current_from, current_to = current
    if max_time - current_from.timestamp() > max_listening_period_s:
        # If updating the current listening period would make it longer
        # than the maximum, create a new listening period that starts
        # just after the current one ends
        new_period_start = current_to.timestamp() + 1
        create_listening_period(new_period_start, max_time)
        return get_latest_listening_period(), new_period_start
    else:
        # Otherwise, update the current listening period to extend to
        # the current time.
        update_listening_period(current_id, max_time)
        return get_latest_listening_period(), current_to.timestamp() + 1



def create_listening_period(from_time, to_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO listening_period (from_time, to_time)
        VALUES (TO_TIMESTAMP(%(ft)s), TO_TIMESTAMP(%(tt)s))
    """, {"ft": from_time, "tt": to_time})
    conn.commit()


def update_listening_period(id, to_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE listening_period
        SET to_time = TO_TIMESTAMP(%(tt)s)
        WHERE id = %(period_id)s
    """, {"period_id": id, "tt": to_time})
    conn.commit()


def get_latest_listening_period():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, from_time, to_time
        FROM listening_period
        WHERE to_time = (
            SELECT MAX(to_time) from listening_period
        )
        LIMIT 1
    """)
    return cursor.fetchone()


def update_play_counts(period_id: int, play_counts: pd.DataFrame):
    print('Updating play counts: ', play_counts)
    conn = get_connection()
    cursor = conn.cursor()
    for _, row in play_counts.iterrows():
        cursor.execute("""
        INSERT INTO listening_history (listening_period_id, track_uri, stream_count)
        VALUES (%(period_id)s, %(track_uri)s, %(stream_count)s)
        ON CONFLICT (listening_period_id, track_uri) DO UPDATE
        SET stream_count = listening_history.stream_count + %(stream_count)s;
        """, {
            "period_id": period_id,
            "track_uri": row["track_uri"],
            "stream_count": row["stream_count"]
        })
    conn.commit()


if __name__ == '__main__':
    save_listening_data()