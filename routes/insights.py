import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text
from routes.utils import to_json


def insights_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        query_params = {
            "wrapped_start_date": params["wrapped_start_date"],
            "wrapped_end_date": params["wrapped_end_date"],
        }
        distributions = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_stream_distributions")),
            conn,
            params=query_params,
        )
        release_months = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_release_month_counts")),
            conn,
        )
        discovery = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_track_discovery_by_month")),
            conn,
            params=query_params,
        )
        variety = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_track_variety_by_month")),
            conn,
            params=query_params,
        )

    return {
        "distributions": to_json(distributions),
        "release_months": to_json(release_months),
        "discovery": to_json(discovery),
        "variety": to_json(variety),
    }
