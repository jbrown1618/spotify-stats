"""
Script to find tracks with zero available markets (potentially deprecated)
and suggest replacements from the database or Spotify API.

Usage:
    python -m script.find_deprecated_tracks
"""

from data.raw import get_connection
from spotify.spotify_client import get_spotify_client


def get_album_url(album_uri):
    """
    Convert a Spotify album URI to a web URL.
    
    Returns album URL string.
    """
    return f"https://open.spotify.com/album/{album_uri.split(':')[-1]}"


def get_deprecated_tracks():
    """
    Get all tracks with 0 available markets.
    
    Returns list of tuples: (track_uri, track_name, isrc, album_uri)
    """
    query = """
    SELECT 
        t.uri,
        t.name,
        t.isrc,
        t.album_uri
    FROM track t
    WHERE t.available_markets_count = 0
    ORDER BY t.name;
    """
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()


def get_playlists_for_track(track_uri):
    """
    Get all playlists that contain the given track.
    
    Returns list of playlist names.
    """
    query = """
    SELECT p.name
    FROM playlist p
    INNER JOIN playlist_track pt ON pt.playlist_uri = p.uri
    WHERE pt.track_uri = %s
    ORDER BY p.name;
    """
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (track_uri,))
        return [row[0] for row in cursor.fetchall()]


def find_replacement_in_db(isrc, deprecated_uri):
    """
    Find a replacement track in the database with the same ISRC and non-zero markets.
    
    Returns tuple: (track_uri, track_name, album_uri, markets_count) or None
    """
    if not isrc:
        return None
    
    query = """
    SELECT 
        t.uri,
        t.name,
        t.album_uri,
        t.available_markets_count
    FROM track t
    WHERE t.isrc = %s
        AND t.uri != %s
        AND t.available_markets_count > 0
    ORDER BY t.available_markets_count DESC
    LIMIT 1;
    """
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (isrc, deprecated_uri))
        result = cursor.fetchone()
        if result:
            return result
        return None


def find_replacement_in_spotify(isrc, deprecated_uri):
    """
    Search Spotify API for a replacement track with the same ISRC.
    
    Returns dict with track info or None
    """
    if not isrc:
        return None
    
    try:
        sp = get_spotify_client()
        results = sp.search(q=f'isrc:{isrc}', type='track', limit=10)
        
        if results and 'tracks' in results and results['tracks']['items']:
            # Find a track with non-empty available_markets
            for track in results['tracks']['items']:
                if track['uri'] != deprecated_uri and len(track.get('available_markets', [])) > 0:
                    return {
                        'uri': track['uri'],
                        'name': track['name'],
                        'album_uri': track['album']['uri'],
                        'album_name': track['album']['name'],
                        'markets_count': len(track.get('available_markets', []))
                    }
        return None
    except Exception as e:
        print(f"Error searching Spotify for ISRC {isrc}: {e}")
        return None


def find_deprecated_tracks():
    """Main function to find and report deprecated tracks."""
    
    print("Finding tracks with zero available markets...")
    deprecated_tracks = get_deprecated_tracks()
    
    if not deprecated_tracks:
        print("No deprecated tracks found! All tracks have at least one available market.")
        return
    
    print(f"Found {len(deprecated_tracks)} potentially deprecated tracks")
    print()
    
    results = []
    
    for track_uri, track_name, isrc, album_uri in deprecated_tracks:
        # Get playlists containing this track
        playlists = get_playlists_for_track(track_uri)
        playlist_str = ", ".join(playlists) if playlists else "None"
        
        # Try to find replacement in database
        replacement = find_replacement_in_db(isrc, track_uri)
        
        if replacement:
            replacement_uri, replacement_name, replacement_album_uri, markets_count = replacement
            replacement_type = "Database"
            replacement_info = f"{replacement_name} ({replacement_uri})"
            replacement_album = get_album_url(replacement_album_uri)
        else:
            # Try to find replacement in Spotify API
            spotify_replacement = find_replacement_in_spotify(isrc, track_uri)
            
            if spotify_replacement:
                replacement_type = "Spotify API"
                replacement_info = f"{spotify_replacement['name']} ({spotify_replacement['uri']})"
                replacement_album = get_album_url(spotify_replacement['album_uri'])
            else:
                replacement_type = "Not Found"
                replacement_info = "No replacement found"
                replacement_album = "N/A"
        
        results.append({
            'Deprecated Track': f"{track_name} ({track_uri})",
            'ISRC': isrc or 'N/A',
            'Replacement Source': replacement_type,
            'Replacement Track': replacement_info,
            'Album Link': replacement_album,
            'In Playlists': playlist_str
        })
    
    # Print results in a nice table format
    print("=" * 120)
    print("DEPRECATED TRACKS REPORT")
    print("=" * 120)
    print()
    
    if results:
        # Print each result in a detailed format
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['Deprecated Track']}")
            print(f"   ISRC: {result['ISRC']}")
            print(f"   Replacement: {result['Replacement Track']} (Source: {result['Replacement Source']})")
            print(f"   Album: {result['Album Link']}")
            print(f"   Playlists: {result['In Playlists']}")
            print()
    
    print("=" * 120)
    print(f"Total deprecated tracks: {len(results)}")
    print("=" * 120)


if __name__ == '__main__':
    find_deprecated_tracks()
