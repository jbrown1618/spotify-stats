"""
Script to reconcile stream counts between the old listening_history table
and the new track_stream table.

For any track where the new table has fewer total streams than the old table,
this script adds random entries to track_stream (within the appropriate period
date ranges) until the totals match.

Usage:
    python -m script.reconcile_stream_counts           # Dry run (default)
    python -m script.reconcile_stream_counts --commit  # Actually commit changes
"""
import sys
import random
from datetime import datetime

from data.raw import get_connection


# Minimum difference threshold - skip tracks with fewer missing streams
MIN_DIFFERENCE_THRESHOLD = 5


def get_track_totals():
    """
    Get total stream counts per track from both old and new tables.
    Only includes tracks where the difference is >= MIN_DIFFERENCE_THRESHOLD.
    
    Returns dict: {track_uri: {'track_name': str, 'old_total': int, 'new_total': int, 'difference': int}}
    """
    query = """
    WITH old_totals AS (
        SELECT 
            track_uri,
            SUM(stream_count) AS old_total
        FROM listening_history
        GROUP BY track_uri
    ),
    new_totals AS (
        SELECT 
            track_uri,
            COUNT(*) AS new_total
        FROM track_stream
        GROUP BY track_uri
    )
    SELECT 
        o.track_uri,
        t.name AS track_name,
        o.old_total,
        COALESCE(n.new_total, 0) AS new_total,
        o.old_total - COALESCE(n.new_total, 0) AS difference
    FROM old_totals o
    LEFT JOIN new_totals n ON o.track_uri = n.track_uri
    LEFT JOIN track t ON t.uri = o.track_uri
    WHERE o.old_total - COALESCE(n.new_total, 0) >= %s
    ORDER BY difference DESC;
    """
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (MIN_DIFFERENCE_THRESHOLD,))
        results = {}
        for track_uri, track_name, old_total, new_total, difference in cursor.fetchall():
            results[track_uri] = {
                'track_name': track_name or 'Unknown',
                'old_total': old_total,
                'new_total': new_total,
                'difference': difference
            }
        return results


def get_periods_for_track(track_uri: str):
    """
    Get all listening periods for a track with their counts from the old table.
    
    Returns list of tuples: (from_time, to_time, stream_count)
    """
    query = """
    SELECT 
        p.from_time,
        p.to_time,
        h.stream_count
    FROM listening_history h
    INNER JOIN listening_period p ON p.id = h.listening_period_id
    WHERE h.track_uri = %s
    ORDER BY p.from_time;
    """
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (track_uri,))
        return cursor.fetchall()


def generate_random_timestamp(from_time: datetime, to_time: datetime) -> datetime:
    """Generate a random timestamp between from_time and to_time."""
    from_ts = from_time.timestamp()
    to_ts = to_time.timestamp()
    random_ts = random.uniform(from_ts, to_ts)
    return datetime.fromtimestamp(random_ts)


def add_streams_for_track(track_uri: str, streams_needed: int, conn, commit: bool = False) -> int:
    """
    Add `streams_needed` random stream entries for the given track.
    Distributes streams across the track's listening periods proportionally.
    
    Returns the number of streams actually added.
    """
    periods = get_periods_for_track(track_uri)
    if not periods:
        return 0
    
    # Calculate total streams in old table to distribute proportionally
    total_old_streams = sum(p[2] for p in periods)
    
    cursor = conn.cursor()
    added = 0
    remaining = streams_needed
    
    for i, (from_time, to_time, period_count) in enumerate(periods):
        if remaining <= 0:
            break
            
        # For the last period, add all remaining; otherwise distribute proportionally
        if i == len(periods) - 1:
            to_add = remaining
        else:
            proportion = period_count / total_old_streams
            to_add = min(remaining, max(1, int(streams_needed * proportion)))
        
        for _ in range(to_add):
            if remaining <= 0:
                break
                
            played_at = generate_random_timestamp(from_time, to_time)
            
            if commit:
                cursor.execute("""
                    INSERT INTO track_stream (track_uri, played_at)
                    VALUES (%s, %s)
                    ON CONFLICT (track_uri, played_at) DO NOTHING
                """, (track_uri, played_at))
                
                if cursor.rowcount > 0:
                    added += 1
                    remaining -= 1
            else:
                # Dry run - just count
                added += 1
                remaining -= 1
    
    return added


def reconcile_stream_counts(commit: bool = False):
    """Main function to reconcile stream counts."""
    print("Finding tracks with discrepancies between listening_history and track_stream...")
    track_totals = get_track_totals()
    
    if not track_totals:
        print("No discrepancies found! All track totals match.")
        return
    
    total_missing = sum(t['difference'] for t in track_totals.values())
    print(f"Found {len(track_totals)} tracks with discrepancies")
    print(f"Total missing streams: {total_missing}")
    print()
    
    if not commit:
        print("DRY RUN (default) - no changes will be made")
        print("Run with --commit to actually add streams")
        print()
    
    # Show a sample of the discrepancies
    print(f"Sample discrepancies (showing first 10, only tracks with >= {MIN_DIFFERENCE_THRESHOLD} missing):")
    print("-" * 80)
    for i, (track_uri, totals) in enumerate(list(track_totals.items())[:10]):
        print(f"  {totals['track_name']} ({track_uri})")
        print(f"    Old total: {totals['old_total']}, New total: {totals['new_total']}, Missing: {totals['difference']}")
    print("-" * 80)
    print()
    
    if commit:
        confirm = input(f"Add up to {total_missing} missing streams? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            return
    
    action = "Adding" if commit else "Would add"
    print(f"{action} missing streams...")
    total_added = 0
    
    with get_connection() as conn:
        for i, (track_uri, totals) in enumerate(track_totals.items()):
            streams_needed = totals['difference']
            track_name = totals['track_name']
            added = add_streams_for_track(track_uri, streams_needed, conn, commit)
            total_added += added
            
            print(f"  [{i + 1}/{len(track_totals)}] {track_name}: {action.lower()} {added} streams (needed {streams_needed})")
            
            if commit and (i + 1) % 100 == 0:
                conn.commit()
        
        if commit:
            conn.commit()
    
    print()
    if commit:
        print(f"Done! Added {total_added} streams.")
        if total_added < total_missing:
            print(f"Note: {total_missing - total_added} streams could not be added (likely due to timestamp conflicts)")
    else:
        print(f"Dry run complete. Would add {total_added} streams.")
        print("Run with --commit to actually add streams.")


if __name__ == '__main__':
    commit = '--commit' in sys.argv
    reconcile_stream_counts(commit=commit)
