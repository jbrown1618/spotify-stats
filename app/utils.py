import json
import typing

import urllib

import pandas as pd


def is_empty_filter(filters):
    return len(filters) == 0


def is_liked_filter(filters):
    return len(filters) == 1 and "liked" in filters


array_filter_keys = ["artists", "albums", "playlists", "labels", "genres", "years"]
def to_filters(args: typing.Mapping[str, str]) -> typing.Mapping[str, typing.Iterable[str]]:
    filters = {
        key: to_array_filter(args.get(key, None))
        for key in array_filter_keys
        if args.get(key, None) is not None
    }

    liked = args.get("liked", None)
    if liked is not None:
        liked = liked.lower() == "true"
        filters["liked"] = liked

    stream_range = args.get("wrapped", None)
    if stream_range is not None:
        values = stream_range.split('..')
        if len(values) == 2:
            filters['min_stream_date'] = values[0]
            filters['max_stream_date'] = values[1]

    return filters


def to_date_range(args: typing.Mapping[str, str]):
    stream_range = args.get("wrapped", None)
    if stream_range is not None:
        values = stream_range.split('..')
        if len(values) == 2:
            return values
    return [None, None]


def to_track_uris(args: typing.Mapping[str, str]) -> typing.Iterable[str]:
    return to_array_filter(args.get('tracks', None))


def to_artist_uris(args: typing.Mapping[str, str]) -> typing.Iterable[str]:
    return to_array_filter(args.get('artists', None))


def to_album_uris(args: typing.Mapping[str, str]) -> typing.Iterable[str]:
    return to_array_filter(args.get('albums', None))


def to_array_filter(arg: str) -> typing.Iterable[str]:
    if arg is None:
        return None
    
    return json.loads(urllib.parse.unquote(arg))


def to_json(df: pd.DataFrame, col: str = None):
    if col is not None:
        index_col = col + '__index'
        df[index_col] = df[col].copy()
        df = df.set_index(index_col)
        return json.loads(df.to_json(orient="index"))
    
    return json.loads(df.to_json(orient="records", index=True))