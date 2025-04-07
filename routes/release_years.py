import typing

from data.query import query_text
from data.raw import get_connection


def release_years_payload(track_uris: typing.Iterable[str]):
    if len(track_uris) == 0:
        return []
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_release_year_track_counts'), 
            { "track_uris": tuple(track_uris) }
        )
        result = cursor.fetchall()

    out = []
    for release_year, track_count, liked_track_count, total_track_count, total_liked_track_count in result:
        out.append({
            "release_year": release_year,
            "track_count": track_count,
            "liked_track_count": liked_track_count,
            "total_track_count": total_track_count,
            "total_liked_track_count": total_liked_track_count
        })

    return out