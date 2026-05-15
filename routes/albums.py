import pandas as pd
import sqlalchemy

from routes.utils import to_json
from data.filters import filtered_connection
from data.query import query_text


def albums_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        # Create the album stream counts temp table within the same connection
        albums = pd.read_sql_query(
            sqlalchemy.text(query_text('select_albums')),
            conn,
            params={
                "wrapped_start_date": params["wrapped_start_date"],
                "wrapped_end_date": params["wrapped_end_date"],
            }
        )
    if albums.empty:
        return {}
    return to_json(albums, 'album_uri')