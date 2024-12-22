import pandas as pd
import sqlalchemy

from data.raw import get_connection, get_engine
from utils.date import this_date

track_score_factor = 0.5
as_of_now = this_date()

get_current_date = '''
SELECT MAX(tt.as_of_date) AS current_date FROM top_track tt;
'''

def current_track_ranks():
    cursor = get_connection().cursor()
    cursor.execute(get_current_date)
    current_date = cursor.fetchone()[0]

    with get_engine().begin() as conn:
        df = pd.read_sql_query(sqlalchemy.text('SELECT track_uri, rank as track_rank, as_of_date  FROM track_rank WHERE as_of_date = :as_of_date;'), conn, params={"as_of_date": str(current_date)})
        return df


def track_ranks_over_time():
    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('SELECT track_uri, rank as track_rank, as_of_date FROM track_rank;'), conn)


def current_artist_ranks():
    cursor = get_connection().cursor()
    cursor.execute(get_current_date)
    current_date = cursor.fetchone()[0]

    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('SELECT artist_uri, rank as artist_rank, as_of_date FROM artist_rank WHERE as_of_date = :as_of_date;'), conn, params={"as_of_date": str(current_date)})


def artist_ranks_over_time():
    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('SELECT artist_uri, rank as artist_rank, as_of_date  FROM artist_rank;'), conn)


def current_album_ranks():
    cursor = get_connection().cursor()
    cursor.execute(get_current_date)
    current_date = cursor.fetchone()[0]

    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('SELECT album_uri, rank as album_rank, as_of_date FROM album_rank WHERE as_of_date = :as_of_date;'), conn, params={"as_of_date": str(current_date)})


def album_ranks_over_time():
    with get_engine().begin() as conn:
        return pd.read_sql_query(sqlalchemy.text('SELECT album_uri, rank as album_rank, as_of_date FROM album_rank;'), conn)


def ensure_ranks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT as_of_date
        FROM top_track
        WHERE as_of_date NOT IN (
            SELECT DISTINCT as_of_date FROM track_rank
        );
    ''')
    unranked_track_dates = [row[0] for row in cursor.fetchall()]

    cursor.execute('''
        SELECT DISTINCT as_of_date
        FROM top_artist
        WHERE as_of_date NOT IN (
            SELECT DISTINCT as_of_date FROM artist_rank
        );
    ''')
    unranked_artist_dates = [row[0] for row in cursor.fetchall()]

    for date in unranked_track_dates:
        print(f'Populating track ranks for {date}')
        cursor.execute(populate_track_ranks, {"as_of_date": date})

    for date in unranked_track_dates:
        print(f'Populating album ranks for {date}')
        cursor.execute(populate_album_ranks, {"as_of_date": date})
    
    for date in unranked_artist_dates:
        print(f'Populating artist ranks for {date}')
        cursor.execute(populate_artist_ranks, {"as_of_date": date})
    
    conn.commit()


track_scores = '''
CREATE TEMPORARY TABLE IF NOT EXISTS track_scores AS
SELECT 
    tt.track_uri,
    tt.as_of_date,
    (CASE
        WHEN tt.term = 'short_term'
            THEN (51 - tt.index)
        WHEN tt.term = 'medium_term'
            THEN 4 * (51 - tt.index)
        WHEN tt.term = 'long_term'
            THEN 8 * (51 - tt.index)
        WHEN tt.term = 'on_repeat'
            THEN 2 * (31 - tt.index)
        WHEN tt.term = 'repeat_rewind'
            THEN 0.5 * (31 - tt.index)
        ELSE 0
    END) AS score
FROM top_track tt;
'''

artist_scores = '''
CREATE TEMPORARY TABLE IF NOT EXISTS artist_scores AS
SELECT 
    ta.artist_uri,
    ta.as_of_date,
    (CASE
        WHEN ta.term = 'short_term'
            THEN (51 - ta.index)
        WHEN ta.term = 'medium_term'
            THEN 4 * (51 - ta.index)
        WHEN ta.term = 'long_term'
            THEN 8 * (51 - ta.index)
        WHEN ta.term = 'on_repeat'
            THEN 2 * (31 - ta.index)
        WHEN ta.term = 'repeat_rewind'
            THEN 0.5 * (31 - ta.index)
        ELSE 0
    END) AS score
FROM top_artist ta;
'''

populate_track_ranks = track_scores + '''
DROP TABLE IF EXISTS total_track_scores;
CREATE TEMPORARY TABLE total_track_scores AS
SELECT 
    track_uri,
    SUM(score) AS total_score
FROM track_scores
WHERE as_of_date <= %(as_of_date)s
GROUP BY track_uri;

INSERT INTO track_rank (track_uri, rank, as_of_date)
SELECT 
    track_uri,
    ROW_NUMBER() OVER(ORDER BY total_score DESC) AS rank,
    %(as_of_date)s as as_of_date
FROM total_track_scores
ORDER BY rank ASC;
'''

populate_artist_ranks = artist_scores + track_scores + '''
DROP TABLE IF EXISTS total_artist_scores;
CREATE TEMPORARY TABLE total_artist_scores AS
SELECT 
    artist_uri,
    SUM(score) AS total_score
FROM artist_scores
WHERE as_of_date <= %(as_of_date)s
GROUP BY artist_uri;

DROP TABLE IF EXISTS track_scores_by_artist;
CREATE TEMPORARY TABLE track_scores_by_artist AS
SELECT
    artist_uri,
    SUM(score) as total_score
FROM track_scores ts
INNER JOIN track_artist ta ON ta.track_uri = ts.track_uri
WHERE as_of_date <= %(as_of_date)s
GROUP BY artist_uri;

DROP TABLE IF EXISTS aggregated_artist_scores;
CREATE TEMPORARY TABLE aggregated_artist_scores AS
SELECT
    COALESCE(tas.artist_uri, tsba.artist_uri) AS artist_uri,
    COALESCE(tas.total_score, 0) + 0.5 * COALESCE(tsba.total_score, 0) AS total_score
FROM total_artist_scores tas
FULL OUTER JOIN track_scores_by_artist tsba 
ON tas.artist_uri = tsba.artist_uri;

INSERT INTO artist_rank (artist_uri, rank, as_of_date)
SELECT 
    artist_uri,
    ROW_NUMBER() OVER(ORDER BY total_score DESC) AS rank,
    %(as_of_date)s as as_of_date
FROM aggregated_artist_scores
ORDER BY rank ASC;
'''

populate_album_ranks = track_scores + '''
DROP TABLE IF EXISTS track_scores_by_album;
CREATE TEMPORARY TABLE track_scores_by_album AS
SELECT
    t.album_uri,
    SUM(ts.score) as total_score
FROM track_scores ts
INNER JOIN track t ON t.uri = ts.track_uri
WHERE as_of_date <= %(as_of_date)s
GROUP BY t.album_uri;

INSERT INTO album_rank (album_uri, rank, as_of_date)
SELECT 
    album_uri,
    ROW_NUMBER() OVER(ORDER BY total_score DESC) AS rank,
    %(as_of_date)s as as_of_date
FROM track_scores_by_album
ORDER BY rank ASC;
'''
