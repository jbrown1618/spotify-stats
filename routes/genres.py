import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text
from routes.pagination import paginate_df, GENRE_SORT_COLUMNS


def genres_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        genres = pd.read_sql_query(
            sqlalchemy.text(query_text('select_genre_track_counts')),
            conn
        )

    if genres.empty:
        return {"items": [], "total": 0}

    genres = genres.rename(columns={
        'genre_track_count': 'track_count',
        'genre_total_track_count': 'total_track_count',
        'genre_liked_track_count': 'liked_track_count',
        'genre_total_liked_track_count': 'total_liked_track_count',
    })

    return paginate_df(genres, filters, GENRE_SORT_COLUMNS, "Most liked tracks")