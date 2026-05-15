import pandas as pd
import sqlalchemy

from routes.utils import to_json
from routes.pagination import paginate_df, ALBUM_SORT_COLUMNS
from data.filters import filtered_connection
from data.query import query_text


def albums_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
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

    paginated = paginate_df(albums, filters, ALBUM_SORT_COLUMNS, "Most streams")
    if paginated is not None:
        return paginated

    return to_json(albums, 'album_uri')