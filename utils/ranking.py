import typing
import pandas as pd
import sqlalchemy

from data.query import query_text
from data.raw import get_connection, get_engine
from utils.date import this_date

track_score_factor = 0.5
as_of_now = this_date()

def current_track_ranks(track_uris: typing.Iterable[str]):
    track_uris = tuple(track_uris) if len(track_uris) > 0 else tuple(['EMPTY'])
    with get_engine().begin() as conn:
        df = pd.read_sql_query(
            sqlalchemy.text(query_text('current_track_ranks')), 
            conn, 
            params={"track_uris": track_uris}
        )
        return df


def track_ranks_over_time(track_uris: typing.Iterable[str]):
    track_uris = tuple(track_uris) if len(track_uris) > 0 else tuple(['EMPTY'])
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('track_ranks_over_time')), 
            conn, 
            params={"track_uris": track_uris}
        )


def current_artist_ranks(artist_uris: typing.Iterable[str]):
    artist_uris = tuple(artist_uris) if len(artist_uris) > 0 else tuple(['EMPTY'])
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('current_artist_ranks')), 
            conn, 
            params={"artist_uris": artist_uris}
        )


def artist_ranks_over_time(artist_uris: typing.Iterable[str]):
    artist_uris = tuple(artist_uris) if len(artist_uris) > 0 else tuple(['EMPTY'])
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('artist_ranks_over_time')), 
            conn, 
            params={"artist_uris": artist_uris}
        )


def current_album_ranks(album_uris: typing.Iterable[str]):
    album_uris = tuple(album_uris) if len(album_uris) > 0 else tuple(['EMPTY'])
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('current_album_ranks')), 
            conn, 
            params={"album_uris": album_uris}
        )


def album_ranks_over_time(album_uris: typing.Iterable[str]):
    album_uris = tuple(album_uris) if len(album_uris) > 0 else tuple(['EMPTY'])
    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text(query_text('album_ranks_over_time')), conn, params={"album_uris": album_uris})


def ensure_ranks(force: bool = False):
    with get_connection() as conn:
        cursor = conn.cursor()

        if force:
            print('Clearing existing ranks...')
            cursor.execute(query_text('truncate_ranks'))
            conn.commit()

        print('Getting dates to populate ranks...')
        cursor.execute(query_text('select_ranking_dates'))
        unranked_dates = [row[0] for row in cursor.fetchall()]

        for date in unranked_dates:
            print(f'Populating track ranks for {date}')
            cursor.execute(query_text('populate_track_ranks'), {"as_of_date": date})

        for date in unranked_dates:
            print(f'Populating album ranks for {date}')
            cursor.execute(query_text('populate_album_ranks'), {"as_of_date": date})
        
        for date in unranked_dates:
            print(f'Populating artist ranks for {date}')
            cursor.execute(query_text('populate_artist_ranks'), {"as_of_date": date})
        
        conn.commit()
