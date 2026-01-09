import json
import typing

import pandas as pd
import sqlalchemy
from routes.utils import to_date_range, to_json
from data.provider import DataProvider
from data.query import query_text
from data.raw import get_engine


def tracks_search_payload(filters: typing.Mapping[str, str]):
    dp = DataProvider()

    min_stream_date, max_stream_date = to_date_range(filters.get("wrapped"))
    tracks = dp.tracks(
        uris=filters.get('tracks', None),
        playlist_uris=filters.get('playlists', None), 
        artist_uris=filters.get('artists', None), 
        album_uris=filters.get('albums', None),
        labels=filters.get('labels', None),
        genres=filters.get('genres', None),
        producers=filters.get('producers', None),
        years=filters.get('years', None),
        liked=filters.get('liked', None),
        start_date=min_stream_date,
        end_date=max_stream_date
    )

    tracks = tracks[['track_uri', 'track_name', 'track_short_name', 'album_release_date', 'album_image_url', 'track_stream_count']]

    return to_json(tracks, 'track_uri')


def track_payload(track_uri, min_date, max_date):
    dp = DataProvider()
    track = dp.track(track_uri, start_date=min_date, end_date=max_date)
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


def track_credits_payload(track_uri):
    with get_engine().begin() as conn:
        credits = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_credits')),
            conn,
            params={'track_uri': track_uri}
        )
        return credits.to_dict('records')