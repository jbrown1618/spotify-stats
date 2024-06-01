import pandas as pd

from data.raw import RawData
from utils.date import this_date

track_score_factor = 0.5
as_of_now = this_date()


def current_track_ranks():
    out = track_ranks_over_time()
    out = out[out['as_of_date'] == out['as_of_date'].max()]
    return out[['track_uri', 'track_rank']].copy()


_track_ranks_over_time = None
def track_ranks_over_time():
    global _track_ranks_over_time


    if _track_ranks_over_time is None:
        out = None

        dates = RawData()['top_tracks']['as_of_date'].unique()
        for as_of_date in dates:
            scores = __track_ranks(as_of=as_of_date)
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
    out = artist_ranks_over_time()
    out = out[out['as_of_date'] == out['as_of_date'].max()]
    return out[['artist_uri', 'artist_rank']].copy()


_artist_ranks_over_time = None
def artist_ranks_over_time():
    global _artist_ranks_over_time

    dates = RawData()['top_artists']['as_of_date'].unique()

    if _artist_ranks_over_time is None:
        out = None

        for as_of_date in dates:
            ranks = __artist_ranks(as_of=as_of_date)
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


def __placement_score(index, term):
    multiplier = 1
    total = 50

    if term == 'on_repeat':
        multiplier = 3
        total = 30
    if term == 'medium_term':
        multiplier = 6
    if term == 'long_term':
        multiplier = 12

    return multiplier * (total + 1 - index)