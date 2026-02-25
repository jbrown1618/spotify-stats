import typing

import sqlalchemy
from data.query import query_text
from data.raw import get_engine


def labels_payload(track_uris: typing.Iterable[str]):
    if len(track_uris) == 0:
        return []
    
    with get_engine().begin() as conn:
        result = conn.execute(
            sqlalchemy.text(query_text('select_label_track_counts')), 
            { "track_uris": tuple(track_uris) }
        )
        rows = result.fetchall()

    out = []
    for label, track_count, total_track_count, liked_track_count, total_liked_track_count in rows:
        out.append({
            "label": label,
            "track_count": track_count,
            "total_track_count": total_track_count,
            "liked_track_count": liked_track_count,
            "total_liked_track_count": total_liked_track_count
        })

    return out