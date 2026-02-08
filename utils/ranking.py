import typing
import pandas as pd
import sqlalchemy

from data.query import query_text
from data.raw import get_engine


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

    out = {}
    for track_uri, year, month, stream_count in results:
        year = int(year)
        month = int(month)
        if track_uri not in out:
            out[track_uri] = {}
        if year not in out[track_uri]:
            out[track_uri][year] = {}
        if month not in out[track_uri][year]:
            out[track_uri][year][month] = stream_count
    return out


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

    out = {}
    for artist_uri, year, month, stream_count in results:
        year = int(year)
        month = int(month)
        if artist_uri not in out:
            out[artist_uri] = {}
        if year not in out[artist_uri]:
            out[artist_uri][year] = {}
        if month not in out[artist_uri][year]:
            out[artist_uri][year][month] = stream_count
    return out


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

    out = {}
    for album_uri, year, month, stream_count in results:
        year = int(year)
        month = int(month)
        if album_uri not in out:
            out[album_uri] = {}
        if year not in out[album_uri]:
            out[album_uri][year] = {}
        if month not in out[album_uri][year]:
            out[album_uri][year][month] = stream_count
    return out