import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text


def labels_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        labels = pd.read_sql_query(
            sqlalchemy.text(query_text('select_label_track_counts')),
            conn
        )

    if labels.empty:
        return []

    out = []
    for _, row in labels.iterrows():
        out.append({
            "label": row['label'],
            "track_count": int(row['label_track_count']),
            "total_track_count": int(row['label_total_track_count']),
            "liked_track_count": int(row['label_liked_track_count']),
            "total_liked_track_count": int(row['label_total_liked_track_count']),
        })

    return out