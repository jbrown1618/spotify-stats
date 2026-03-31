import typing

import pandas as pd
import sqlalchemy

from data.query import query_text
from data.raw import get_engine


def release_years_payload(track_uris: typing.Iterable[str]):
    if len(track_uris) == 0:
        return []
    
    with get_engine().begin() as conn:
        result = pd.read_sql_query(
            sqlalchemy.text(query_text('select_release_year_track_counts')),
            conn,
            params={"track_uris": tuple(track_uris)}
        )

    out = []
    for _, row in result.iterrows():
        out.append({
            "release_year": int(row['release_year']),
            "track_count": row['track_count'],
            "liked_track_count": row['liked_track_count'],
            "total_track_count": row['total_track_count'],
            "total_liked_track_count": row['total_liked_track_count']
        })

    return out