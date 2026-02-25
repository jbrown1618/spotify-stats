import typing

import pandas as pd
import sqlalchemy

from data.query import query_text
from data.raw import get_engine


def labels_payload(track_uris: typing.Iterable[str]):
    if len(track_uris) == 0:
        return []
    
    with get_engine().begin() as conn:
        result = pd.read_sql_query(
            sqlalchemy.text(query_text('select_label_track_counts')),
            conn,
            params={"track_uris": tuple(track_uris)}
        )

    out = []
    for _, row in result.iterrows():
        out.append({
            "label": row['label'],
            "track_count": row['label_track_count'],
            "total_track_count": row['label_total_track_count'],
            "liked_track_count": row['label_liked_track_count'],
            "total_liked_track_count": row['label_total_liked_track_count']
        })

    return out