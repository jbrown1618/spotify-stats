"""
Script to clean up orphan track streams.

This handles the case where track_stream contains URIs that were superseded by
repair_orphan_tracks. Since the reconciliation script ran after import, there may
be duplicate streams: some for the old (orphan) URI and some for the new (canonical) URI.

This script:
1. Finds track URIs in track_stream that are not in playlist_track
2. Looks them up via the Spotify API to get title/artist info
3. Checks if we have a matching track (by name/artist) in our database
4. If the matching track also has streams, deletes the orphan's streams

Usage:
    python -m script.cleanup_orphan_streams           # Dry run (default)
    python -m script.cleanup_orphan_streams --commit  # Actually delete orphan streams
"""
import sys

from data.repository import DataRepository
from spotify.spotify_client import get_spotify_client


repository = DataRepository()


def lookup_tracks_batch(sp, uris: list[str]) -> dict:
    """
    Look up track info from Spotify API in batches.
    Returns dict: {uri: {'name': str, 'artist': str} or None if not found}
    """
    results = {}
    batch_size = 50
    
    for i in range(0, len(uris), batch_size):
        batch = uris[i:i + batch_size]
        print(f"Looking up {len(batch)} tracks from Spotify API...")
        
        try:
            response = sp.tracks(batch)
            for uri, track in zip(batch, response['tracks']):
                if track is None:
                    results[uri] = None
                else:
                    artist_name = track['artists'][0]['name'] if track['artists'] else None
                    results[uri] = {
                        'name': track['name'],
                        'artist': artist_name
                    }
        except Exception as e:
            print(f"Error looking up tracks: {e}")
            for uri in batch:
                results[uri] = None
    
    return results


def cleanup_orphan_streams(commit: bool = False):
    """Main function to clean up orphan streams."""
    print("Finding orphan track URIs in track_stream...")
    orphan_uris = repository.orphan_stream_uris()
    print(f"Found {len(orphan_uris)} track URIs in track_stream not in any playlist")
    
    if not orphan_uris:
        print("No orphan streams to clean up.")
        return
    
    # Look up track info from Spotify
    sp = get_spotify_client()
    track_info = lookup_tracks_batch(sp, orphan_uris)
    
    total_deleted = 0
    tracks_deleted = 0
    
    for orphan_uri in orphan_uris:
        info = track_info.get(orphan_uri)
        
        if info is None:
            # Track not found on Spotify (may have been removed)
            continue
        
        track_name = info['name']
        artist_name = info['artist']
        
        if not track_name or not artist_name:
            continue
        
        # Look for a matching track in our database
        match = repository.matching_track_by_name_artist(
            track_name,
            artist_name,
        )
        
        if match is None:
            # No matching track in our database
            continue
        
        matching_uri, matching_name = match
        
        # Check if the matching track has streams
        matching_streams = repository.track_stream_count(matching_uri)
        
        if matching_streams == 0:
            # Matching track has no streams, so we can't delete the orphan's
            continue
        
        # We have a match with streams - delete the orphan's streams
        orphan_streams = repository.track_stream_count(orphan_uri)
        
        action = "Deleting" if commit else "Would delete"
        print(f"{action} {orphan_streams} streams for orphan track '{track_name}' ({orphan_uri})")
        print(f"  -> Canonical track: {matching_uri} has {matching_streams} streams")
        
        if commit:
            repository.delete_streams_for_track(orphan_uri, commit=True)
        
        total_deleted += orphan_streams
        tracks_deleted += 1
    
    if commit:
        print(f"\nDeleted {total_deleted} streams from {tracks_deleted} orphan tracks")
    else:
        print(f"\nWould delete {total_deleted} streams from {tracks_deleted} orphan tracks")
        print("Run with --commit to apply changes")


if __name__ == '__main__':
    commit = '--commit' in sys.argv
    cleanup_orphan_streams(commit=commit)
