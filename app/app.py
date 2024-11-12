import json
import typing
import urllib
import pandas as pd
from flask import Flask, send_file, request

from data.provider import DataProvider

pd.options.mode.chained_assignment = None  # default='warn'
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
    labels = filters.get('labels', None)
    genres = filters.get('genres', None)
    liked = filters.get('liked', None)

    return {
        "filter_options": get_filter_options(filters),
        "playlists": to_json(dp.playlists(
            uris=playlist_uris, 
            artist_uris=artist_uris,
            album_uris=album_uris,
            labels=labels,
            genres=genres
        ), 'playlist_uri'),
        "tracks": to_json(dp.tracks(
            playlist_uris=playlist_uris, 
            artist_uris=artist_uris, 
            album_uris=album_uris,
            labels=labels,
            genres=genres,
            liked=liked
        ), 'track_uri'),
        "artists": to_json(dp.artists(
            uris=artist_uris,
            album_uris=album_uris,
            playlist_uris=playlist_uris,
            labels=labels,
            genres=genres,
            with_liked_tracks=liked
        ), 'artist_uri'),
        "albums": to_json(dp.albums(
            uris=album_uris,
            artist_uris=artist_uris,
            playlist_uris=playlist_uris,
            labels=labels,
            genres=genres
        ), 'album_uri'),
        "labels": [l for l in dp.labels(
            label_names=labels,
            album_uris=album_uris,
            artist_uris=artist_uris,
            playlist_uris=playlist_uris,
            liked=liked
        )['album_standardized_label']],
        "genres": [g for g in dp.genres(
            names=genres,
            playlist_uris=playlist_uris,
            artist_uris=artist_uris,
            album_uris=album_uris,
            labels=labels,
            with_liked_tracks=liked
        )]
    }


def get_filter_options(filters):
    dp = DataProvider()
    artist_uris = filters.get('artists', None)
    album_uris = filters.get('albums', None)
    playlist_uris = filters.get('playlists', None)
    labels = filters.get('labels', None)
    genres = filters.get('genres', None)
    liked = filters.get('liked', None)
    return {
        "artists": to_json(dp.artists(
            album_uris=album_uris, 
            playlist_uris=playlist_uris,
            labels=labels,
            genres=genres,
            with_liked_tracks=liked
        )[['artist_uri', 'artist_name']], 'artist_uri'),
        "albums": to_json(dp.albums(
            artist_uris=artist_uris, 
            playlist_uris=playlist_uris,
            labels=labels,
            genres=genres
        )[['album_uri', 'album_name']], 'album_uri'),
        "playlists": to_json(dp.playlists(
            artist_uris=artist_uris, 
            album_uris=album_uris,
            labels=labels,
            genres=genres
        )[['playlist_uri', 'playlist_name']], 'playlist_uri'),
        "labels": [l for l in dp.labels(
            album_uris=album_uris,
            artist_uris=artist_uris,
            playlist_uris=playlist_uris,
            genres=genres,
            liked=liked
        )['album_standardized_label']],
        "genres": [g for g in dp.genres(
            playlist_uris=playlist_uris,
            artist_uris=artist_uris,
            album_uris=album_uris,
            labels=labels,
            with_liked_tracks=liked
        )]
    }


array_filter_keys = ["artists", "albums", "playlists", "labels", "genres"]
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


def to_json(df: pd.DataFrame, col: str):
    index_col = col + '__index'
    df[index_col] = df[col].copy()
    df = df.set_index(index_col)
    return json.loads(df.to_json(orient="index", index=True))