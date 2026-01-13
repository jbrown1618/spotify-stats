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

from data.raw import get_connection
from spotify.spotify_client import get_spotify_client


def get_orphan_stream_uris():
    """
    Get track URIs that exist in track_stream but not in playlist_track.
    These are potential orphans that may have been superseded.
    """
    query = """
    SELECT DISTINCT ts.track_uri
    FROM track_stream ts
    LEFT JOIN playlist_track pt ON pt.track_uri = ts.track_uri
    WHERE pt.track_uri IS NULL
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]


def get_stream_count(track_uri: str) -> int:
    """Get the number of streams for a track."""
    query = "SELECT COUNT(*) FROM track_stream WHERE track_uri = %s"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (track_uri,))
        return cursor.fetchone()[0]


def find_matching_track(track_name: str, artist_name: str):
    """
    Find a track in our database that matches by name and primary artist.
    Returns (uri, name) or None if no match found.
    """
    query = """
    SELECT t.uri, t.name
    FROM track t
    INNER JOIN track_artist ta ON ta.track_uri = t.uri AND ta.artist_index = 0
    INNER JOIN artist a ON a.uri = ta.artist_uri
    INNER JOIN playlist_track pt ON pt.track_uri = t.uri
    WHERE t.name = %s AND a.name = %s
    LIMIT 1
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (track_name, artist_name))
        return cursor.fetchone()


def delete_streams_for_track(track_uri: str, commit: bool = False):
    """Delete all streams for a given track URI."""
    query = "DELETE FROM track_stream WHERE track_uri = %s"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (track_uri,))
        if commit:
            conn.commit()
        else:
            conn.rollback()


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
    orphan_uris = get_orphan_stream_uris()
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
        match = find_matching_track(track_name, artist_name)
        
        if match is None:
            # No matching track in our database
            continue
        
        matching_uri, matching_name = match
        
        # Check if the matching track has streams
        matching_streams = get_stream_count(matching_uri)
        
        if matching_streams == 0:
            # Matching track has no streams, so we can't delete the orphan's
            continue
        
        # We have a match with streams - delete the orphan's streams
        orphan_streams = get_stream_count(orphan_uri)
        
        action = "Deleting" if commit else "Would delete"
        print(f"{action} {orphan_streams} streams for orphan track '{track_name}' ({orphan_uri})")
        print(f"  -> Canonical track: {matching_uri} has {matching_streams} streams")
        
        if commit:
            delete_streams_for_track(orphan_uri, commit=True)
        
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
