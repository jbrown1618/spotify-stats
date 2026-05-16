import typing
import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text
from data.raw import get_connection, get_engine
from routes.utils import to_json


def track_ranks_over_time(track_uris: typing.Iterable[str], from_date, to_date):
    track_uris = tuple(track_uris) if len(track_uris) > 0 else tuple(['EMPTY'])
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('track_ranks_over_time')), 
            conn, 
            params={
                "track_uris": track_uris,
                "from_date": from_date,
                "to_date": to_date
            }
        )


def artist_ranks_over_time(artist_uris: typing.Iterable[str], from_date, to_date):
    artist_uris = tuple(artist_uris) if len(artist_uris) > 0 else tuple(['EMPTY'])
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('artist_ranks_over_time')), 
            conn, 
            params={
                "artist_uris": artist_uris,
                "from_date": from_date,
                "to_date": to_date
            }
        )


def album_ranks_over_time(album_uris: typing.Iterable[str], from_date, to_date):
    album_uris = tuple(album_uris) if len(album_uris) > 0 else tuple(['EMPTY'])
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('album_ranks_over_time')), 
            conn, 
            params={
                "album_uris": album_uris,
                "from_date": from_date,
                "to_date": to_date
            })


def track_streams_by_month(track_uris, from_date, to_date):
    top_track_uris = tuple(track_uris) if len(track_uris) > 0 else tuple(['EMPTY'])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_track_streams_by_month'), 
            {
                "track_uris": top_track_uris,
                "from_date": from_date,
                "to_date": to_date
            }
        )
        results = cursor.fetchall()

    return _streams_by_month_dict(
        results, 0,
        metadata_fields=["track_short_name", "track_name", "album_image_url"],
    )


def artist_streams_by_month(artist_uris, from_date, to_date):
    top_artist_uris = tuple(artist_uris) if len(artist_uris) > 0 else tuple(['EMPTY'])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_artist_streams_by_month'),
            {
                "artist_uris": top_artist_uris,
                "from_date": from_date,
                "to_date": to_date
            }
        )
        results = cursor.fetchall()

    return _streams_by_month_dict(
        results, 0,
        metadata_fields=["artist_name", "artist_image_url"],
    )


def album_streams_by_month(album_uris, from_date, to_date):
    top_album_uris = tuple(album_uris) if len(album_uris) > 0 else tuple(['EMPTY'])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_album_streams_by_month'),
            {
                "album_uris": top_album_uris,
                "from_date": from_date,
                "to_date": to_date
            }
        )
        results = cursor.fetchall()

    return _streams_by_month_dict(
        results, 0,
        metadata_fields=["album_short_name", "album_name", "album_image_url"],
    )


# --- Filter-based variants (server-side top-N selection) ---

def filtered_track_ranks_over_time(filters: dict, n: int = 10):
    with filtered_connection(filters) as (conn, params):
        return pd.read_sql_query(
            sqlalchemy.text(query_text('filtered_track_ranks_over_time')),
            conn,
            params={
                "from_date": params["wrapped_start_date"],
                "to_date": params["wrapped_end_date"],
                "n": n,
            }
        )


def filtered_track_streams_by_month(filters: dict, n: int = 5):
    with filtered_connection(filters) as (conn, params):
        df = pd.read_sql_query(
            sqlalchemy.text(query_text('filtered_track_streams_by_month')),
            conn,
            params={
                "from_date": params["wrapped_start_date"],
                "to_date": params["wrapped_end_date"],
                "n": n,
            }
        )
    return _streams_by_month_dict_from_df(
        df,
        metadata_columns=["track_short_name", "track_name", "album_image_url"],
    )


def filtered_artist_ranks_over_time(filters: dict, n: int = 10):
    with filtered_connection(filters) as (conn, params):
        return pd.read_sql_query(
            sqlalchemy.text(query_text('filtered_artist_ranks_over_time')),
            conn,
            params={
                "from_date": params["wrapped_start_date"],
                "to_date": params["wrapped_end_date"],
                "n": n,
            }
        )


def filtered_artist_streams_by_month(filters: dict, n: int = 5):
    with filtered_connection(filters) as (conn, params):
        df = pd.read_sql_query(
            sqlalchemy.text(query_text('filtered_artist_streams_by_month')),
            conn,
            params={
                "from_date": params["wrapped_start_date"],
                "to_date": params["wrapped_end_date"],
                "n": n,
            }
        )
    return _streams_by_month_dict_from_df(
        df,
        metadata_columns=["artist_name", "artist_image_url"],
    )


def filtered_album_ranks_over_time(filters: dict, n: int = 10):
    with filtered_connection(filters) as (conn, params):
        return pd.read_sql_query(
            sqlalchemy.text(query_text('filtered_album_ranks_over_time')),
            conn,
            params={
                "from_date": params["wrapped_start_date"],
                "to_date": params["wrapped_end_date"],
                "n": n,
            }
        )


def filtered_album_streams_by_month(filters: dict, n: int = 5):
    with filtered_connection(filters) as (conn, params):
        df = pd.read_sql_query(
            sqlalchemy.text(query_text('filtered_album_streams_by_month')),
            conn,
            params={
                "from_date": params["wrapped_start_date"],
                "to_date": params["wrapped_end_date"],
                "n": n,
            }
        )
    return _streams_by_month_dict_from_df(
        df,
        metadata_columns=["album_short_name", "album_name", "album_image_url"],
    )


def _streams_by_month_dict(results, uri_index, metadata_fields=None):
    """Convert raw cursor results (uri, year, month, count, ...) to nested dict with metadata."""
    streams = {}
    metadata = {}
    for row in results:
        uri = row[uri_index]
        year = int(row[1])
        month = int(row[2])
        stream_count = row[3]
        if uri not in streams:
            streams[uri] = {}
        if year not in streams[uri]:
            streams[uri][year] = {}
        if month not in streams[uri][year]:
            streams[uri][year][month] = stream_count

        if metadata_fields and uri not in metadata:
            metadata[uri] = {
                field: row[4 + i]
                for i, field in enumerate(metadata_fields)
            }

    return {"streams": streams, "metadata": metadata}


def _streams_by_month_dict_from_df(df, metadata_columns=None):
    """Convert a DataFrame to nested streams dict plus optional metadata."""
    streams = {}
    metadata = {}
    for _, row in df.iterrows():
        uri = row.iloc[0]
        year = int(row.iloc[1])
        month = int(row.iloc[2])
        stream_count = int(row.iloc[3])
        if uri not in streams:
            streams[uri] = {}
        if year not in streams[uri]:
            streams[uri][year] = {}
        if month not in streams[uri][year]:
            streams[uri][year][month] = stream_count

        if metadata_columns and uri not in metadata:
            metadata[uri] = {col: row[col] for col in metadata_columns if col in row.index}

    if metadata_columns:
        return {"streams": streams, "metadata": metadata}
    return streams
