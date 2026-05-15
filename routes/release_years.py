import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text
from routes.pagination import paginate_df, RELEASE_YEAR_SORT_COLUMNS


def release_years_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        years = pd.read_sql_query(
            sqlalchemy.text(query_text('select_release_year_track_counts')),
            conn
        )

    if years.empty:
        return []

    paginated = paginate_df(years, filters, RELEASE_YEAR_SORT_COLUMNS, "Most liked tracks")
    if paginated is not None:
        return paginated

    out = []
    for _, row in years.iterrows():
        out.append({
            "release_year": int(row['release_year']),
            "track_count": int(row['track_count']),
            "liked_track_count": int(row['liked_track_count']),
            "total_track_count": int(row['total_track_count']),
            "total_liked_track_count": int(row['total_liked_track_count']),
        })

    return out