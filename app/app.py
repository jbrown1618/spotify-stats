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


@app.route("/data")
def data():
    dp = DataProvider()

    filters = to_filters(request.args)

    return {
        "filters": filters,
        "tracks": to_json(dp.tracks(artist_uris=filters.get("artists")).head(100)),
        "artists": to_json(dp.artists(uris=filters.get("artists")).head(100))
    }


filter_keys = ["artists", "albums"]

def to_filters(args: typing.Mapping[str, str]) -> typing.Mapping[str, typing.Iterable[str]]:
    return {
        key: to_filter(args.get(key, None))
        for key in filter_keys
    }


def to_filter(arg: str) -> typing.Iterable[str]:
    if arg is None:
        return None
    
    return json.loads(urllib.parse.unquote(arg))


def to_json(df: pd.DataFrame):
    return json.loads(df.to_json(orient="records"))