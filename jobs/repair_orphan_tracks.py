from data.raw import get_connection
from utils.ranking import ensure_ranks

def repair_orphan_tracks():
    did_update = False
    print('Identifying orphan tracks...')
    for orphan_uri, orphan_name in get_orphan_tracks():
        matching_track = get_matching_track(orphan_uri)
        if matching_track is None:
            print(f"No match found for '{orphan_name}'")
            continue

        matching_uri, matching_name = matching_track
        print(f"Repairing '{matching_name}'...")
        repair_orphan(orphan_uri, matching_uri)
        did_update = True
    
    if did_update:
        print('Recalculating track and album ranks...')
        recalculate_ranks()

    delete_orphan_albums()
    delete_orphan_artists()
    print('Done repairing orphan tracks')


def get_orphan_tracks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT distinct tt.track_uri, t.name
        FROM top_track tt
        INNER JOIN track t ON t.uri = tt.track_uri
        WHERE tt.track_uri NOT IN (
            SELECT pt.track_uri FROM playlist_track pt
        )
        UNION ALL (
            SELECT distinct h.track_uri, t.name
            FROM listening_history h
            INNER JOIN track t ON t.uri = h.track_uri
            WHERE h.track_uri NOT IN (
                SELECT pt.track_uri FROM playlist_track pt
            )
        );
    ''')
    return cursor.fetchall()


def get_matching_track(track_uri):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.uri, t.name
        FROM track t
        INNER JOIN track_artist ta ON ta.track_uri = t.uri AND ta.artist_index = 0
        INNER JOIN track orphan ON orphan.uri = %(orphan_uri)s
        INNER JOIN track_artist orphanta ON orphanta.track_uri = orphan.uri AND orphanta.artist_index = 0
        WHERE t.name = orphan.name AND ta.artist_uri = orphanta.artist_uri AND t.uri IN (
            SELECT pt.track_uri FROM playlist_track pt
        );
    ''', {"orphan_uri": track_uri})
    return cursor.fetchone()


def repair_orphan(orphan_uri, replacement_uri):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE listening_history
        SET track_uri = %(replacement_uri)s
        WHERE track_uri = %(orphan_uri)s;

        UPDATE top_track
        SET track_uri = %(replacement_uri)s
        WHERE track_uri = %(orphan_uri)s;

        UPDATE sp_track_mb_recording
        SET spotify_track_uri = %(replacement_uri)s
        WHERE spotify_track_uri = %(orphan_uri)s;

        DELETE FROM track
        WHERE uri = %(orphan_uri)s;

        DELETE FROM track_artist
        WHERE track_uri = %(orphan_uri)s;
    """, {"orphan_uri": orphan_uri, "replacement_uri": replacement_uri})
    conn.commit()


def delete_orphan_albums():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM album
        WHERE uri NOT IN (
            SELECT DISTINCT album_uri
            FROM track
        );
    """)
    conn.commit()


def delete_orphan_artists():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM artist
        WHERE uri NOT IN (
            SELECT DISTINCT artist_uri
            FROM track_artist
        );
    """)
    conn.commit()


def recalculate_ranks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        TRUNCATE track_rank;
        TRUNCATE album_rank;
    """)
    conn.commit()

    ensure_ranks()


if __name__ == '__main__':
    repair_orphan_tracks()