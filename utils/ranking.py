import pandas as pd
import sqlalchemy

from data.raw import get_connection, get_engine
from utils.date import this_date

track_score_factor = 0.5
as_of_now = this_date()

def current_track_ranks():
    with get_engine().begin() as conn:
        df = pd.read_sql_query(sqlalchemy.text('''
            SELECT track_uri, rank as track_rank, stream_count as track_stream_count, as_of_date
            FROM track_rank
            WHERE as_of_date = (
                SELECT MAX(as_of_date) FROM track_rank
            );
        '''), conn)
        return df


def track_ranks_over_time():
    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('''
            SELECT track_uri, rank as track_rank, stream_count as track_stream_count, as_of_date
            FROM track_rank;
        '''), conn)


def current_artist_ranks():
    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('''
            SELECT artist_uri, rank as artist_rank, stream_count as artist_stream_count, as_of_date
            FROM artist_rank
            WHERE as_of_date = (
                SELECT MAX(as_of_date) FROM artist_rank
            );
        '''), conn)


def artist_ranks_over_time():
    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('''
            SELECT artist_uri, rank as artist_rank, stream_count as artist_stream_count, as_of_date
            FROM artist_rank;
        '''), conn)


def current_album_ranks():
    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('''
            SELECT album_uri, rank as album_rank, stream_count as album_stream_count, as_of_date
            FROM album_rank
            WHERE as_of_date = (
                SELECT MAX(as_of_date) FROM album_rank
            );
        '''), conn)


def album_ranks_over_time():
    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('''
            SELECT album_uri, rank as album_rank, stream_count as album_stream_count, as_of_date
            FROM album_rank;
        '''), conn)


def ensure_ranks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT to_time
        FROM listening_period
        WHERE to_time NOT IN (
            SELECT DISTINCT as_of_date FROM track_rank
        );
    ''')
    unranked_dates = [row[0] for row in cursor.fetchall()]

    for date in unranked_dates:
        print(f'Populating track ranks for {date}')
        cursor.execute(populate_track_ranks, {"as_of_date": date})

    for date in unranked_dates:
        print(f'Populating album ranks for {date}')
        cursor.execute(populate_album_ranks, {"as_of_date": date})
    
    for date in unranked_dates:
        print(f'Populating artist ranks for {date}')
        cursor.execute(populate_artist_ranks, {"as_of_date": date})
    
    conn.commit()


populate_track_ranks = '''
DROP TABLE IF EXISTS total_track_streams_for_date;
CREATE TEMPORARY TABLE total_track_streams_for_date AS
SELECT h.track_uri,
       SUM(stream_count) as stream_count
FROM listening_history h
INNER JOIN listening_period p ON p.id = h.listening_period_id
WHERE p.from_time <= %(as_of_date)s
GROUP BY h.track_uri;

INSERT INTO track_rank (track_uri, stream_count, rank, as_of_date)
SELECT track_uri,
       stream_count,
       ROW_NUMBER() OVER(ORDER BY stream_count DESC) AS rank,
       %(as_of_date)s as as_of_date
FROM total_track_streams_for_date
ON CONFLICT DO NOTHING;
'''

populate_artist_ranks = '''
DROP TABLE IF EXISTS total_artist_streams_for_date;
CREATE TEMPORARY TABLE total_artist_streams_for_date AS
SELECT ta.artist_uri,
       SUM(stream_count) as stream_count
FROM listening_history h
INNER JOIN listening_period p ON p.id = h.listening_period_id
INNER JOIN track_artist ta ON ta.track_uri = h.track_uri
WHERE p.from_time <= %(as_of_date)s
GROUP BY ta.artist_uri;

INSERT INTO artist_rank (artist_uri, stream_count, rank, as_of_date)
SELECT artist_uri,
       stream_count,
       ROW_NUMBER() OVER(ORDER BY stream_count DESC) AS rank,
       %(as_of_date)s as as_of_date
FROM total_artist_streams_for_date
ON CONFLICT DO NOTHING;
'''

populate_album_ranks = '''
DROP TABLE IF EXISTS total_album_streams_for_date;
CREATE TEMPORARY TABLE total_album_streams_for_date AS
SELECT t.album_uri,
       SUM(stream_count) as stream_count
FROM listening_history h
INNER JOIN listening_period p ON p.id = h.listening_period_id
INNER JOIN track t ON t.uri = h.track_uri
WHERE p.from_time <= %(as_of_date)s
GROUP BY t.album_uri;

INSERT INTO album_rank (album_uri, stream_count, rank, as_of_date)
SELECT album_uri,
       stream_count,
       ROW_NUMBER() OVER(ORDER BY stream_count DESC) AS rank,
       %(as_of_date)s as as_of_date
FROM total_album_streams_for_date
ON CONFLICT DO NOTHING;
'''
