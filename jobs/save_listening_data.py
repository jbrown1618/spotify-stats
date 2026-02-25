from datetime import datetime
import pandas as pd
import sqlalchemy
from data.query import query_text
from data.raw import get_engine
from jobs.queue import queue_job
from jobs.save_spotify_data import save_tracks_by_uri
from spotify.spotify_client import get_spotify_client
from utils.track import is_blacklisted

played_at_date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
alternate_date_format = "%Y-%m-%dT%H:%M:%SZ"


def save_listening_data():
    sp = get_spotify_client()
    print("Fetching recent listening history...")
    recents = sp.current_user_recently_played(limit=50)

    plays_data = []
    for recent_play in recents['items']:
        track = recent_play['track']
        track_name = track['name']
        if is_blacklisted(track_name):
            print(f"Skipping blacklisted track: {track_name}")
            continue
        track_uri = track['uri']
        played_at = recent_play['played_at']
        time = to_timestamp(played_at)
        plays_data.append({"track_uri": track_uri, "time": time})
    plays = pd.DataFrame(plays_data)

    if len(plays) == 0:
        print("No non-blacklisted tracks to save")
        return

    save_streams(plays)

    unsaved_uris = get_unsaved_track_uris()
    if len(unsaved_uris) > 0:
        save_tracks_by_uri(unsaved_uris)
        queue_job("repair_orphan_tracks")


def to_timestamp(date_str: str) -> float:
    try:
        return datetime.strptime(date_str, played_at_date_format).timestamp()
    except ValueError:
        return datetime.strptime(date_str, alternate_date_format).timestamp()


def save_streams(plays: pd.DataFrame):
    """Save individual streams to the track_stream table."""
    print(f'Saving {len(plays)} streams to track_stream table...')
    with get_engine().begin() as conn:
        for _, row in plays.iterrows():
            conn.execute(
                sqlalchemy.text(query_text('insert_stream')),
                {
                    "track_uri": row["track_uri"],
                    "played_at": row["time"]
                }
            )


def get_unsaved_track_uris():
    with get_engine().begin() as conn:
        result = conn.execute(sqlalchemy.text(query_text('select_streams_without_tracks')))
        return [row[0] for row in result.fetchall()]


if __name__ == '__main__':
    save_listening_data()
