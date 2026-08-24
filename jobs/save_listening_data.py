from datetime import datetime

import pandas as pd

from data.repository import DataRepository
from jobs.queue import queue_job
from jobs.save_spotify_data import save_tracks_by_uri
from spotify.spotify_client import get_spotify_client
from utils.track import is_blacklisted


played_at_date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
alternate_date_format = "%Y-%m-%dT%H:%M:%SZ"
repository = DataRepository()


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
        return {
            "recent_plays_fetched": len(recents["items"]),
            "streams_inserted": 0,
            "tracks_skipped": len(recents["items"]),
            "track_metadata_saved": 0,
            "repair_jobs_queued": 0,
        }

    inserted_streams = save_streams(plays)

    unsaved_uris = repository.track_uris_without_metadata()
    track_metadata_saved = 0
    repair_jobs_queued = 0
    if len(unsaved_uris) > 0:
        metadata_summary = save_tracks_by_uri(unsaved_uris)
        track_metadata_saved = metadata_summary["tracks"]
        queue_job("repair_orphan_tracks")
        repair_jobs_queued = 1

    return {
        "recent_plays_fetched": len(recents["items"]),
        "streams_inserted": inserted_streams,
        "tracks_skipped": len(recents["items"]) - len(plays),
        "track_metadata_saved": track_metadata_saved,
        "repair_jobs_queued": repair_jobs_queued,
    }


def to_timestamp(date_str: str) -> float:
    try:
        return datetime.strptime(date_str, played_at_date_format).timestamp()
    except ValueError:
        return datetime.strptime(date_str, alternate_date_format).timestamp()


def save_streams(plays: pd.DataFrame):
    """Save individual streams to the track_stream table."""
    print(f'Saving {len(plays)} streams to track_stream table...')
    return repository.save_streams(
        {
            "track_uri": row["track_uri"],
            "played_at": row["time"],
        }
        for _, row in plays.iterrows()
    )
if __name__ == '__main__':
    save_listening_data()
