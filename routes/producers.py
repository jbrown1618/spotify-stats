import pandas as pd
import sqlalchemy

from routes.pagination import paginate_df, PRODUCER_SORT_COLUMNS
from data.filters import filtered_connection
from data.query import query_text


def producers_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        producers = pd.read_sql_query(
            sqlalchemy.text(query_text('select_producers')),
            conn
        )
    if producers.empty:
        return {"items": [], "total": 0}
    producers.drop_duplicates(subset=['producer_mbid'], keep='first', inplace=True)

    return paginate_df(producers, filters, PRODUCER_SORT_COLUMNS, "Most tracks")