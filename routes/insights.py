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
        total_streams = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_total_streams_by_month")),
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
        weekday_by_month = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_weekday_by_month_heatmap")),
            conn,
            params=query_params,
        )
        month_by_year = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_month_by_year_heatmap")),
            conn,
            params=query_params,
        )
        hour_by_weekday = pd.read_sql_query(
            sqlalchemy.text(query_text("filtered_hour_by_weekday_heatmap")),
            conn,
            params=query_params,
        )

    return {
        "distributions": to_json(distributions),
        "total_streams": to_json(total_streams),
        "release_months": to_json(release_months),
        "discovery": to_json(discovery),
        "variety": to_json(variety),
        "weekday_by_month": to_json(weekday_by_month),
        "month_by_year": to_json(month_by_year),
        "hour_by_weekday": to_json(hour_by_weekday),
    }
