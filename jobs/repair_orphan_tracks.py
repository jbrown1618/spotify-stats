import sqlalchemy
from data.query import query_text
from data.raw import get_engine

def repair_orphan_tracks():
    print('Identifying orphan tracks...')
    for orphan_uri, _ in get_orphan_tracks():
        matching_track = get_matching_track(orphan_uri)
        if matching_track is None:
            continue

        matching_uri, matching_name = matching_track
        print(f"Repairing '{matching_name}'...")
        repair_orphan(orphan_uri, matching_uri)

    delete_orphan_albums()
    delete_orphan_artists()
    print('Done repairing orphan tracks')


def get_orphan_tracks():
    with get_engine().begin() as conn:
        result = conn.execute(sqlalchemy.text(query_text('select_orphan_tracks')))
        return result.fetchall()


def get_matching_track(track_uri):
    with get_engine().begin() as conn:
        result = conn.execute(sqlalchemy.text(query_text('select_matching_track')), {"orphan_uri": track_uri})
        return result.fetchone()


def repair_orphan(orphan_uri, replacement_uri):
    with get_engine().begin() as conn:
        conn.execute(
            sqlalchemy.text(query_text('repair_orphan_track')), 
            {"orphan_uri": orphan_uri, "replacement_uri": replacement_uri}
        )


def delete_orphan_albums():
    with get_engine().begin() as conn:
        conn.execute(sqlalchemy.text(query_text('delete_orphan_albums')))


def delete_orphan_artists():
    with get_engine().begin() as conn:
        conn.execute(sqlalchemy.text(query_text('delete_orphan_artists')))


if __name__ == '__main__':
    repair_orphan_tracks()