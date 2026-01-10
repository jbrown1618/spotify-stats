"""
This script imports extended listening history from a Spotify data request into the track_stream table.

It takes a directory path as input and imports all JSON files matching the pattern:
Streaming_History_Audio_*.json

Only streams before the cutoff timestamp (earliest existing stream in the database) will be imported
to avoid duplicates.

Usage:
    python -m script.import_track_streams /path/to/spotify/data/directory
"""
import sys
import os
import json
import re
from datetime import datetime

from data.query import query_text
from data.raw import get_connection
from utils.track import is_blacklisted


# Pattern for Spotify extended streaming history files
FILENAME_PATTERN = re.compile(r'^Streaming_History_Audio_.*\.json$')

# Cutoff: ignore any streams at or after this timestamp (earliest existing stream)
CUTOFF_TIMESTAMP = datetime(2026, 1, 3, 19, 47, 11, 356000)

# Date format in the Spotify export files
PLAYED_AT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def find_streaming_history_files(directory: str) -> list[str]:
    """Find all Streaming_History_Audio_*.json files in the given directory."""
    files = []
    for filename in os.listdir(directory):
        if FILENAME_PATTERN.match(filename):
            files.append(os.path.join(directory, filename))
    return sorted(files)


def parse_timestamp(ts_str: str) -> datetime:
    """Parse timestamp string from Spotify export format."""
    return datetime.strptime(ts_str, PLAYED_AT_DATE_FORMAT)


def import_streams_from_file(filepath: str, conn) -> tuple[int, int]:
    """
    Import streams from a single JSON file.
    
    Returns tuple of (imported_count, skipped_count)
    """
    print(f"Processing {filepath}...")
    
    with open(filepath) as f:
        records = json.load(f)
    
    cursor = conn.cursor()
    imported = 0
    skipped = 0
    
    for record in records:
        # Skip records without a track URI (podcasts, etc.)
        track_uri = record.get('spotify_track_uri')
        if not track_uri:
            skipped += 1
            continue
        
        # Skip blacklisted tracks
        track_name = record.get('master_metadata_track_name')
        if track_name and is_blacklisted(track_name):
            skipped += 1
            continue
        
        # Parse timestamp and skip if at or after cutoff
        ts_str = record.get('ts')
        if not ts_str:
            skipped += 1
            continue
            
        played_at = parse_timestamp(ts_str)
        if played_at >= CUTOFF_TIMESTAMP:
            skipped += 1
            continue
        
        # Insert the stream
        cursor.execute(
            query_text('insert_stream'),
            {
                "track_uri": track_uri,
                "played_at": played_at.timestamp()
            }
        )
        imported += 1
    
    return imported, skipped


def import_track_streams(directory: str):
    """Import all streaming history from the given directory."""
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    files = find_streaming_history_files(directory)
    if not files:
        print(f"No Streaming_History_Audio_*.json files found in {directory}")
        sys.exit(1)
    
    print(f"Found {len(files)} streaming history file(s):")
    for f in files:
        print(f"  - {os.path.basename(f)}")
    print()
    
    total_imported = 0
    total_skipped = 0
    
    with get_connection() as conn:
        for filepath in files:
            imported, skipped = import_streams_from_file(filepath, conn)
            total_imported += imported
            total_skipped += skipped
            print(f"  Imported: {imported}, Skipped: {skipped}")
        
        print()
        print(f"Committing {total_imported} streams to database...")
        conn.commit()
    
    print()
    print(f"Import complete!")
    print(f"  Total imported: {total_imported}")
    print(f"  Total skipped: {total_skipped}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m script.import_track_streams <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    import_track_streams(directory)
