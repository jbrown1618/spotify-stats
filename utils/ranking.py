import pandas as pd

from data.raw import RawData


_current_track_scores = None
_current_artist_scores = None
_track_scores_over_time = None
_artist_scores_over_time = None


def track_ranks():
    return __calculate_track_ranks()


def track_ranks_over_time():
    global _track_scores_over_time

    dates = RawData()['top_tracks']['as_of_date'].unique()

    if _track_scores_over_time is None:
        out = None

        print('Calculating track scores over time...')
        for as_of_date in dates:
            print('    ' + as_of_date + '...')
            scores = __calculate_track_ranks(as_of=as_of_date)
            scores['as_of_date'] = as_of_date
            out = scores if out is None else pd.concat([out, scores])
        _track_scores_over_time = out.reset_index()
        print('Done!')

    return _track_scores_over_time


def __calculate_track_ranks(as_of: str=None):
    global _current_track_scores

    top_tracks = RawData()['top_tracks'].copy()

    if as_of is None and _current_track_scores is not None:
        return _current_track_scores
    
    if as_of is not None:
        top_tracks = top_tracks[top_tracks['as_of_date'] <= as_of]

    top_tracks['track_score'] = top_tracks.apply(lambda row: placement_score(row['index'], row['term']), axis=1)

    out = top_tracks.groupby('track_uri')\
        .agg({'track_score': 'sum'})\
        .reset_index()
    
    out = out.sort_values('track_score', ascending=False)

    out['track_score_rank'] = [i + 1 for i in range(len(out))]

    if as_of is None and _current_track_scores is None:
        _current_track_scores = out

    return out


def artist_ranks():
    return __calculate_artist_ranks()


def artist_ranks_over_time():
    global _artist_scores_over_time

    dates = RawData()['top_artists']['as_of_date'].unique()

    if _artist_scores_over_time is None:
        out = None

        print('Calculating artist scores over time...')
        for as_of_date in dates:
            print('    ' + as_of_date + '...')
            scores = __calculate_artist_ranks(as_of=as_of_date)
            scores['as_of_date'] = as_of_date
            out = scores if out is None else pd.concat([out, scores])
        _artist_scores_over_time = out.reset_index()
        print('Done!')

    return _artist_scores_over_time


def __calculate_artist_ranks(as_of: str=None):
    global _current_artist_scores

    top_artists = RawData()['top_artists'].copy()

    if as_of is None and _current_artist_scores is not None:
        return _current_artist_scores
    
    if as_of is not None:
        top_artists = top_artists[top_artists['as_of_date'] <= as_of]

    top_artists['artist_score'] = top_artists.apply(lambda row: placement_score(row['index'], row['term']), axis=1)

    out = top_artists.groupby('artist_uri')\
        .agg({'artist_score': 'sum'})\
        .reset_index()
    
    out = out.sort_values('artist_score', ascending=False)

    out['artist_score_rank'] = [i + 1 for i in range(len(out))]

    if as_of is None and _current_artist_scores is None:
        _current_artist_scores = out

    return out


def placement_score(index, term):
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