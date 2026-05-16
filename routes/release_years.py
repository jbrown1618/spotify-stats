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
        return {"items": [], "total": 0}

    return paginate_df(years, filters, RELEASE_YEAR_SORT_COLUMNS, "Most liked tracks")