import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text
from routes.utils import to_json


def artist_stream_share_by_month_payload(filters: dict):
    n = filters.get("n", 10)
    with filtered_connection(filters) as (conn, params):
        rows = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_artist_stream_share_by_month")),
            conn,
            params={
                "n": n,
                "wrapped_start_date": params["wrapped_start_date"],
                "wrapped_end_date": params["wrapped_end_date"],
            },
        )
    return to_json(rows)


def genre_stream_share_by_month_payload(filters: dict):
    n = filters.get("n", 10)
    with filtered_connection(filters) as (conn, params):
        rows = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_genre_stream_share_by_month")),
            conn,
            params={
                "n": n,
                "wrapped_start_date": params["wrapped_start_date"],
                "wrapped_end_date": params["wrapped_end_date"],
            },
        )
    return to_json(rows)
