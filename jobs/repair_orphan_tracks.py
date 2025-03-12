from data.query import query_text
from data.raw import get_connection
from jobs.queue import queue_job

def repair_orphan_tracks():
    did_update = False
    print('Identifying orphan tracks...')
    for orphan_uri, _ in get_orphan_tracks():
        matching_track = get_matching_track(orphan_uri)
        if matching_track is None:
            continue

        matching_uri, matching_name = matching_track
        print(f"Repairing '{matching_name}'...")
        repair_orphan(orphan_uri, matching_uri)
        did_update = True
    
    if did_update:
        print('Recalculating track and album ranks...')
        queue_job("ensure_ranks", { "force": True })

    delete_orphan_albums()
    delete_orphan_artists()
    print('Done repairing orphan tracks')


def get_orphan_tracks():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_text('select_orphan_tracks'))
        return cursor.fetchall()


def get_matching_track(track_uri):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_text('select_matching_track'), {"orphan_uri": track_uri})
        return cursor.fetchone()


def repair_orphan(orphan_uri, replacement_uri):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('repair_orphan_track'), 
            {"orphan_uri": orphan_uri, "replacement_uri": replacement_uri}
        )
        conn.commit()


def delete_orphan_albums():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_text('delete_orphan_albums'))
        conn.commit()


def delete_orphan_artists():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_text('delete_orphan_artists'))
        conn.commit()


if __name__ == '__main__':
    repair_orphan_tracks()