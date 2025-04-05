import typing

from data.query import query_text
from data.raw import get_connection


def labels_payload(track_uris: typing.Iterable[str]):
    if len(track_uris) == 0:
        return {}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_label_track_counts'), 
            { "track_uris": tuple(track_uris) }
        )
        result = cursor.fetchall()

    out = {}
    for label, label_track_count, label_total_track_count, label_liked_track_count, label_total_liked_track_count in result:
        out[label] = {
            "label": label,
            "label_track_count": label_track_count,
            "label_total_track_count": label_total_track_count,
            "label_liked_track_count": label_liked_track_count,
            "label_total_liked_track_count": label_total_liked_track_count
        }

    return out