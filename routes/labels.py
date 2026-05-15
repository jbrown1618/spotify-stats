import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text
from routes.pagination import paginate_df, LABEL_SORT_COLUMNS


def labels_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        labels = pd.read_sql_query(
            sqlalchemy.text(query_text('select_label_track_counts')),
            conn
        )

    if labels.empty:
        return []

    labels = labels.rename(columns={
        'label_track_count': 'track_count',
        'label_total_track_count': 'total_track_count',
        'label_liked_track_count': 'liked_track_count',
        'label_total_liked_track_count': 'total_liked_track_count',
    })

    paginated = paginate_df(labels, filters, LABEL_SORT_COLUMNS, "Most liked tracks")
    if paginated is not None:
        return paginated

    out = []
    for _, row in labels.iterrows():
        out.append({
            "label": row['label'],
            "track_count": int(row['track_count']),
            "total_track_count": int(row['total_track_count']),
            "liked_track_count": int(row['liked_track_count']),
            "total_liked_track_count": int(row['total_liked_track_count']),
        })

    return out