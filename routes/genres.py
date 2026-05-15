import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text


def genres_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        genres = pd.read_sql_query(
            sqlalchemy.text(query_text('select_genre_track_counts')),
            conn
        )

    if genres.empty:
        return []

    out = []
    for _, row in genres.iterrows():
        out.append({
            "genre": row['genre'],
            "track_count": int(row['genre_track_count']),
            "total_track_count": int(row['genre_total_track_count']),
            "liked_track_count": int(row['genre_liked_track_count']),
            "total_liked_track_count": int(row['genre_total_liked_track_count']),
        })

    return out