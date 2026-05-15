import pandas as pd
import sqlalchemy

from routes.utils import to_json
from routes.pagination import paginate_df, PLAYLIST_SORT_COLUMNS
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

    paginated = paginate_df(playlists, filters, PLAYLIST_SORT_COLUMNS, "Most liked tracks")
    if paginated is not None:
        return paginated

    return to_json(playlists, 'playlist_uri')