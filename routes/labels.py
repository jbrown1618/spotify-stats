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
        return {"items": [], "total": 0}

    labels = labels.rename(columns={
        'label_track_count': 'track_count',
        'label_total_track_count': 'total_track_count',
        'label_liked_track_count': 'liked_track_count',
        'label_total_liked_track_count': 'total_liked_track_count',
    })

    return paginate_df(labels, filters, LABEL_SORT_COLUMNS, "Most liked tracks")