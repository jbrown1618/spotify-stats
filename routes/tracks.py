import json
import typing

import pandas as pd
import sqlalchemy
from routes.utils import to_json
from data.provider import DataProvider
from data.query import query_text
from data.raw import get_engine


def tracks_search_payload(filters: typing.Mapping[str, str]):
    dp = DataProvider()

    min_stream_date = filters.get('min_stream_date', None)
    max_stream_date = filters.get('max_stream_date', None)

    filtered_track_uris = filters.get('tracks', None)

    top_track_uris = None
    if min_stream_date is not None and max_stream_date is not None:
        top_track_uris = top_tracks(min_stream_date, max_stream_date)

    track_uris = None if filtered_track_uris is None and top_track_uris is None \
        else filtered_track_uris if filtered_track_uris is not None and top_track_uris is None \
        else top_track_uris if filtered_track_uris is None and top_track_uris is not None \
        else set(top_track_uris).intersection(filtered_track_uris)

    tracks = dp.tracks(
        uris=track_uris,
        playlist_uris=filters.get('playlists', None), 
        artist_uris=filters.get('artists', None), 
        album_uris=filters.get('albums', None),
        labels=filters.get('labels', None),
        genres=filters.get('genres', None),
        producers=filters.get('producers', None),
        years=filters.get('years', None),
        liked=filters.get('liked', None)
    )

    tracks = tracks[['track_uri', 'track_name', 'track_short_name', 'album_release_date', 'album_image_url', 'track_stream_count']]

    return to_json(tracks, 'track_uri')


def track_payload(track_uri):
    dp = DataProvider()
    track = dp.track(track_uri)
    return json.loads(track.to_json())


def top_tracks(from_date, to_date):
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('select_top_tracks_for_date_range')), 
            conn, 
            params={ 
                'min_stream_date': from_date, 
                'max_stream_date': to_date
            }
        )['track_uri']