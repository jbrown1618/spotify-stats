import json
from app.utils import to_json
from data.provider import DataProvider


def tracks_search_payload(filters):

    dp = DataProvider()

    tracks = dp.tracks(
        playlist_uris=filters.get('playlists', None), 
        artist_uris=filters.get('artists', None), 
        album_uris=filters.get('albums', None),
        labels=filters.get('labels', None),
        genres=filters.get('genres', None),
        years=filters.get('years', None),
        liked=filters.get('liked', None)
    )

    tracks = tracks[['track_uri', 'track_name', 'album_release_date', 'album_image_url', 'track_stream_count']]

    return to_json(tracks, 'track_uri')


def track_payload(track_uri):
    dp = DataProvider()
    track = dp.track(track_uri)
    return json.loads(track.to_json())