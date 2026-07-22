import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text


DEFAULT_PERCENTILE_MIN = 90
DEFAULT_PERCENTILE_MAX = 100
RECOMMENDATION_LIMIT = 20


def recommendations_payload(filters: dict):
    percentile_min, percentile_max = _parse_percentile_range(filters)

    with filtered_connection(filters) as (conn, filter_params):
        recommendation_tracks = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_recommendations_by_percentile_range')),
            conn,
            params={
                'percentile_min': percentile_min / 100,
                'percentile_max': percentile_max / 100,
                'limit': RECOMMENDATION_LIMIT,
                "wrapped_start_date": filter_params["wrapped_start_date"],
                "wrapped_end_date": filter_params["wrapped_end_date"],
            }
        )

    return {
        "type": "track",
        "uris": recommendation_tracks['track_uri'].tolist()
    }


def _parse_percentile_range(filters: dict) -> tuple[int, int]:
    percentile_min = int(filters.get('stream_percentile_min', DEFAULT_PERCENTILE_MIN))
    percentile_max = int(filters.get('stream_percentile_max', DEFAULT_PERCENTILE_MAX))

    if percentile_min < 0 or percentile_min > 100:
        raise ValueError('stream_percentile_min must be between 0 and 100')
    if percentile_max < 0 or percentile_max > 100:
        raise ValueError('stream_percentile_max must be between 0 and 100')
    if percentile_min > percentile_max:
        raise ValueError('stream_percentile_min must be less than or equal to stream_percentile_max')

    return percentile_min, percentile_max
