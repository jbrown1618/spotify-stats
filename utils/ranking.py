import pandas as pd
import sqlalchemy

from data.raw import RawData, get_connection, get_engine
from utils.date import this_date
from utils.settings import data_mode

track_score_factor = 0.5
as_of_now = this_date()

get_current_date = '''
SELECT MAX(tt.as_of_date) AS current_date FROM top_track tt;
'''

def current_track_ranks():
    if data_mode() == 'sql':
        cursor = get_connection().cursor()
        cursor.execute(get_current_date)
        current_date = cursor.fetchone()[0]

        with get_engine().begin() as conn:
            df = pd.read_sql_query(sqlalchemy.text('SELECT track_uri, rank as track_rank, as_of_date  FROM track_rank WHERE as_of_date = :as_of_date;'), conn, params={"as_of_date": str(current_date)})
            return df
        
    out = track_ranks_over_time()
    out = out[out['as_of_date'] == out['as_of_date'].max()]
    return out[['track_uri', 'track_rank']].copy()


_track_ranks_over_time = None
def track_ranks_over_time():
    global _track_ranks_over_time

    if _track_ranks_over_time is None:
        if data_mode() == 'sql':
            with get_engine().begin() as conn:
                _track_ranks_over_time = pd.read_sql_query(sqlalchemy.text('SELECT track_uri, rank as track_rank, as_of_date FROM track_rank;'), conn)
                return _track_ranks_over_time
            
        out = None

        dates = RawData()['top_tracks']['as_of_date'].unique()
        for as_of_date in dates:
            scores = __track_ranks(as_of=str(as_of_date))
            scores['as_of_date'] = as_of_date
            out = scores if out is None else pd.concat([out, scores])
        _track_ranks_over_time = out.reset_index()

    return _track_ranks_over_time


def __track_ranks(as_of: str=as_of_now):
    placement_scores = __track_placement_scores(as_of)
    placement_scores.rename(columns={'track_placement_score': 'track_score'}, inplace=True)

    out = placement_scores.sort_values('track_score', ascending=False)
    out.fillna(0, inplace=True)
    out['track_rank'] = [i + 1 for i in range(len(out))]

    return out[['track_uri', 'track_rank']].copy()


_track_placement_scores_memo = {}
def __track_placement_scores(as_of: str=as_of_now):
    cached = _track_placement_scores_memo.get(as_of, None)
    if cached is not None:
        return cached
    
    print(f'Calculating track placement scores for {as_of}...')

    top_tracks = RawData()['top_tracks'].copy()
    top_tracks = top_tracks[top_tracks['as_of_date'] <= as_of]

    top_tracks['track_placement_score'] = top_tracks.apply(lambda row: __placement_score(row['index'], row['term']), axis=1)

    out = top_tracks.groupby('track_uri')\
        .agg({'track_placement_score': 'sum'})\
        .reset_index()
    
    _track_placement_scores_memo[as_of] = out
    return out


def current_artist_ranks():
    if data_mode() == 'sql':
        cursor = get_connection().cursor()
        cursor.execute(get_current_date)
        current_date = cursor.fetchone()[0]

        with get_engine().begin() as conn:
            df = pd.read_sql_query(sqlalchemy.text('SELECT artist_uri, rank as artist_rank, as_of_date FROM artist_rank WHERE as_of_date = :as_of_date;'), conn, params={"as_of_date": str(current_date)})
            return df

    out = artist_ranks_over_time()
    out = out[out['as_of_date'] == out['as_of_date'].max()]
    return out[['artist_uri', 'artist_rank']].copy()


_artist_ranks_over_time = None
def artist_ranks_over_time():
    global _artist_ranks_over_time

    if _artist_ranks_over_time is None:
        if data_mode() == 'sql':
            with get_engine().begin() as conn:
                _artist_ranks_over_time = pd.read_sql_query(sqlalchemy.text('SELECT artist_uri, rank as artist_rank, as_of_date  FROM artist_rank;'), conn)
                return _artist_ranks_over_time
            
        out = None

        dates = RawData()['top_artists']['as_of_date'].unique()
        for as_of_date in dates:
            ranks = __artist_ranks(as_of=str(as_of_date))
            ranks['as_of_date'] = as_of_date
            out = ranks if out is None else pd.concat([out, ranks])
        _artist_ranks_over_time = out.reset_index()

    return _artist_ranks_over_time


def __artist_ranks(as_of: str=as_of_now):
    placement_scores = __artist_placement_scores(as_of)
        
    track_scores = __track_placement_scores(as_of)
    track_artist = RawData()['track_artist']

    track_scores_by_artist = pd.merge(track_scores, track_artist, on="track_uri")\
        .groupby("artist_uri")\
        .agg({'track_placement_score': 'sum'})
    
    all_scores = pd.merge(placement_scores, track_scores_by_artist, on="artist_uri", how="outer")
    all_scores.fillna(0, inplace=True)
    all_scores['artist_score'] = all_scores['artist_placement_score'] + all_scores['track_placement_score'] * track_score_factor

    out = all_scores.sort_values('artist_score', ascending=False)
    out['artist_rank'] = [i + 1 for i in range(len(out))]

    return out[['artist_uri', 'artist_rank']].copy()


_artist_placement_scores_memo = {}
def __artist_placement_scores(as_of: str=as_of_now):
    cached = _artist_placement_scores_memo.get(as_of, None)
    if cached is not None:
        return cached
    
    print(f'Calculating artist placement scores for {as_of}...')

    top_artists = RawData()['top_artists'].copy()
    top_artists = top_artists[top_artists['as_of_date'] <= as_of]

    top_artists['artist_placement_score'] = top_artists.apply(lambda row: __placement_score(row['index'], row['term']), axis=1)

    out = top_artists.groupby('artist_uri')\
        .agg({'artist_placement_score': 'sum'})\
        .reset_index()

    _artist_placement_scores_memo[as_of] = out
    return out


def current_album_ranks():
    if data_mode() == 'sql':
        cursor = get_connection().cursor()
        cursor.execute(get_current_date)
        current_date = cursor.fetchone()[0]

        with get_engine().begin() as conn:
            df = pd.read_sql_query(sqlalchemy.text('SELECT album_uri, rank as album_rank, as_of_date FROM album_rank WHERE as_of_date = :as_of_date;'), conn, params={"as_of_date": str(current_date)})
            return df

    out = album_ranks_over_time()
    out = out[out['as_of_date'] == out['as_of_date'].max()]
    return out[['album_uri', 'album_rank']].copy()


_album_ranks_over_time = None
def album_ranks_over_time():
    global _album_ranks_over_time

    if _album_ranks_over_time is None:
        if data_mode() == 'sql':
            with get_engine().begin() as conn:
                _album_ranks_over_time = pd.read_sql_query(sqlalchemy.text('SELECT album_uri, rank as album_rank, as_of_date FROM album_rank;'), conn)
                return _album_ranks_over_time
            
        out = None

        dates = RawData()['top_tracks']['as_of_date'].unique()
        for as_of_date in dates:
            ranks = __album_ranks(as_of=str(as_of_date))
            ranks['as_of_date'] = as_of_date
            out = ranks if out is None else pd.concat([out, ranks])
        _album_ranks_over_time = out.reset_index()

    return _album_ranks_over_time


def __album_ranks(as_of: str=as_of_now):
    track_scores = __track_placement_scores(as_of)
    tracks = RawData()['tracks']

    album_scores = pd.merge(track_scores, tracks, on="track_uri")\
        .groupby("album_uri")\
        .agg({'track_placement_score': 'sum'})\
        .reset_index()
    
    album_scores.fillna(0, inplace=True)
    album_scores['album_score'] = album_scores['track_placement_score']

    out = album_scores.sort_values('album_score', ascending=False)
    out['album_rank'] = [i + 1 for i in range(len(out))]

    return out[['album_uri', 'album_rank']].copy()


def __placement_score(index, term):
    multiplier = 1
    total = 50

    if term == 'on_repeat':
        multiplier = 2
        total = 30

    if term == 'repeat_rewind':
        multiplier = 0.5
        total = 30

    if term == 'short_term':
        multiplier = 1
        total = 50

    if term == 'medium_term':
        multiplier = 4
        total = 50

    if term == 'long_term':
        multiplier = 8
        total = 50

    return multiplier * (total + 1 - index)


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
