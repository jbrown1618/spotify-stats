import json
import typing
import urllib
import pandas as pd
from flask import Flask, send_file, request

from data.provider import DataProvider

app = Flask(__name__)


@app.route("/")
def index():
    return send_file("./static/index.html")


@app.route("/api/summary")
def data():
    dp = DataProvider()

    filters = to_filters(request.args)
    artist_uris = filters.get('artists', None)
    album_uris = filters.get('albums', None)
    playlist_uris = filters.get('playlists', None)
    liked = filters.get('liked', None)

    return {
        "filters": filters,
        "filter_options": get_filter_options(filters),
        "playlists": to_json(dp.playlists(
            uris=playlist_uris, 
            artist_uris=artist_uris,
            album_uris=album_uris
        ), 'playlist_uri'),
        "tracks": to_json(dp.tracks(
            playlist_uris=playlist_uris, 
            artist_uris=artist_uris, 
            album_uris=album_uris,
            liked=liked
        ), 'track_uri'),
        "artists": to_json(dp.artists(
            uris=artist_uris,
            album_uris=album_uris,
            playlist_uris=playlist_uris,
            with_liked_tracks=liked
        ), 'artist_uri'),
        "albums": to_json(dp.albums(
            uris=album_uris,
            artist_uris=artist_uris,
            playlist_uris=playlist_uris
        ), 'album_uri')
    }


def get_filter_options(filters):
    artist_uris = filters.get('artists', None)
    album_uris = filters.get('albums', None)
    playlist_uris = filters.get('playlists', None)
    return {
        "artists": to_json(DataProvider().artists(
            album_uris=album_uris, 
            playlist_uris=playlist_uris
        )[['artist_uri', 'artist_name']], 'artist_uri'),
        "albums": to_json(DataProvider().albums(
            artist_uris=artist_uris, 
            playlist_uris=playlist_uris
        )[['album_uri', 'album_name']], 'album_uri'),
        "playlists": to_json(DataProvider().playlists(
            artist_uris=artist_uris, 
            album_uris=album_uris
        )[['playlist_uri', 'playlist_name']], 'playlist_uri')
    }


array_filter_keys = ["artists", "albums", "playlists"]
def to_filters(args: typing.Mapping[str, str]) -> typing.Mapping[str, typing.Iterable[str]]:
    filters = {
        key: to_array_filter(args.get(key, None))
        for key in array_filter_keys
    }

    liked = args.get("liked", None)
    if liked is not None:
        liked = liked.lower() == "true"
    filters["liked"] = liked

    return filters


def to_array_filter(arg: str) -> typing.Iterable[str]:
    if arg is None:
        return None
    
    return json.loads(urllib.parse.unquote(arg))


def to_json(df: pd.DataFrame, index_col: str):
    df[index_col + '__index'] = df[index_col].copy()
    df = df.set_index(index_col + '__index')
    return json.loads(df.to_json(orient="index", index=True))