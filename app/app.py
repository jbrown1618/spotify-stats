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


@app.route("/api/data")
def data():
    dp = DataProvider()

    filters = to_filters(request.args)
    artist_uris = filters.get('artists', None)

    return {
        "filters": filters,
        "filter_options": get_filter_options(),
        "playlists": to_json(dp.playlists(artist_uris=artist_uris), 'playlist_uri'),
        "tracks": to_json(dp.tracks(artist_uris=artist_uris), 'track_uri'),
        "artists": to_json(dp.artists(uris=artist_uris), 'artist_uri')
    }


filter_keys = ["artists", "albums"]

def get_filter_options():
    return {
        "artists": to_json(DataProvider().artists()[['artist_uri', 'artist_name']], 'artist_uri'),
        "albums": [],
        "playlists": []
    }

def to_filters(args: typing.Mapping[str, str]) -> typing.Mapping[str, typing.Iterable[str]]:
    return {
        key: to_filter(args.get(key, None))
        for key in filter_keys
    }


def to_filter(arg: str) -> typing.Iterable[str]:
    if arg is None:
        return None
    
    return json.loads(urllib.parse.unquote(arg))


def to_json(df: pd.DataFrame, index_col: str):
    df = df.set_index(index_col)
    return json.loads(df.to_json(orient="index", index=True))