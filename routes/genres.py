import typing

from data.query import query_text
from data.raw import get_connection


def genres_payload(track_uris: typing.Iterable[str]):
    if track_uris is None or len(track_uris) == 0:
        return []
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_genre_track_counts'), 
            { "track_uris": tuple(track_uris) }
        )
        result = cursor.fetchall()

    out = []
    for genre, track_count, total_track_count, liked_track_count, total_liked_track_count in result:
        out.append({
            "genre": genre,
            "track_count": track_count,
            "liked_track_count": liked_track_count,
            "total_track_count": total_track_count,
            "total_liked_track_count": total_liked_track_count
        })

    return out