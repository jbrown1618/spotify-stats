import pandas as pd
import sqlalchemy

from routes.utils import to_json
from data.filters import filtered_connection
from data.query import query_text


def playlists_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        playlists = pd.read_sql_query(
            sqlalchemy.text(query_text('select_playlists')),
            conn
        )
    if playlists.empty:
        return {}
    return to_json(playlists, 'playlist_uri')