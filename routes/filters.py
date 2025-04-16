from routes.utils import to_json
from data.provider import DataProvider


__cache_filter_options = None

def filter_options_payload():
    global __cache_filter_options

    if __cache_filter_options is not None:
        return __cache_filter_options
    
    dp = DataProvider()
    tracks = dp.tracks(liked=True)
    playlists = dp.playlists(track_uris=tracks['track_uri'])
    artists = dp.artists(track_uris=tracks['track_uri'])
    albums = dp.albums(track_uris=tracks['track_uri'])
    labels = dp.labels(album_uris=albums['album_uri'])
    __cache_filter_options = {
            "artists": to_json(artists[['artist_uri', 'artist_name']], 'artist_uri'),
            "albums": to_json(albums[['album_uri', 'album_name']], 'album_uri'),
            "playlists": to_json(playlists[['playlist_uri', 'playlist_name']], 'playlist_uri'),
            "producers": {}, # TODO
            "labels": labels,
            "genres": dp.genres(artist_uris=artists['artist_uri']),
            "years": [y for y in albums['album_release_year'].unique()]
        }
    
    return __cache_filter_options