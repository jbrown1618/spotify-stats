import typing

import pandas as pd
import sqlalchemy

from data.database import get_engine
from data.filters import filtered_connection
from data.query import query_text
from routes.pagination import TRACK_SORT_COLUMNS, paginate_df
from routes.utils import to_json


def tracks_search_payload(filters: typing.Mapping[str, str]):
    with filtered_connection(filters) as (conn, params):
        tracks = pd.read_sql_query(
            sqlalchemy.text(query_text('select_filtered_tracks')),
            conn,
            params={
                "wrapped_start_date": params["wrapped_start_date"],
                "wrapped_end_date": params["wrapped_end_date"],
            }
        )

    return paginate_df(tracks, filters, TRACK_SORT_COLUMNS, "Most streams")


def top_tracks(from_date, to_date):
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('select_top_tracks_for_date_range')), 
            conn, 
            params={ 
                'min_stream_date': from_date, 
                'max_stream_date': to_date
            }
        )['track_uri']


def track_credits_payload(track_uri):
    with get_engine().begin() as conn:
        credits = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_credits')),
            conn,
            params={'track_uri': track_uri}
        )
        return to_json(credits)