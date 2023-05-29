from datetime import datetime
import pandas as pd

from data.provider import DataProvider

categorical_cols = ['audio_time_signature', 'audio_mode', 'audio_key', 'album_type']
date_cols = ['album_release_date', 'album_release_year']

def prepare_ml_data():
    dp = DataProvider()
    
    tracks = dp.tracks()

    tracks = pd.merge(tracks, prepare_track_genre(), on="track_uri")
    tracks = pd.merge(tracks, prepare_album_label(), on="album_uri")
    tracks = tracks.set_index('track_uri')

    cols_to_drop = [col for col in tracks.columns if should_drop(col, tracks)]
    tracks.drop(columns=cols_to_drop, inplace=True)

    tracks = pd.get_dummies(tracks, columns=categorical_cols)

    tracks['album_release_timestamp'] = tracks['album_release_date'].apply(date_to_timestamp)
    tracks.drop(columns=date_cols, inplace=True)

    for col in tracks.columns:
        if tracks[col].dtype == bool:
            tracks[col] = tracks[col].replace({True: 1, False: 0})

    return tracks


def date_to_timestamp(d: str):
    if len(d) == 10:
        return datetime.strptime(d, '%Y-%m-%d').timestamp()

    if len(d) == 7:
        return datetime.strptime(d + '-01', '%Y-%m-%d').timestamp()
    
    if len(d) == 4:
        return datetime.strptime(d + '-01-01', '%Y-%m-%d').timestamp()
    
    return 0


def prepare_track_genre():
    track_genre = DataProvider().track_genre()[['track_uri', 'genre']]
    track_genre = pd.get_dummies(track_genre, columns=["genre"], prefix="has_genre")
    track_genre = track_genre.groupby('track_uri').agg("sum").reset_index()

    return track_genre


def prepare_album_label():
    album_label = DataProvider().album_label()[['album_uri', 'album_standardized_label']]
    album_label = pd.get_dummies(album_label, columns=['album_standardized_label'], prefix="has_label")
    album_label = album_label.groupby('album_uri').agg("sum").reset_index()

    return album_label


def should_drop(col, tracks):
    if col == 'album_label':
        return True
    
    if col.startswith('has_') and tracks[col].sum() < 10:
        return True
    
    if col.endswith('_name'):
        return True
    
    if col.endswith('_uri'):
        return True
    
    if col.endswith('_image_url'):
        return True
    
    return False
