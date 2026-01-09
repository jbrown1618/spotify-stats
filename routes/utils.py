import json
import typing

import urllib

import pandas as pd


def is_empty_filter(filters):
    return len(filters) == 0


def is_liked_filter(filters):
    return len(filters) == 1 and "liked" in filters


def to_date_range(stream_range: str):
    if stream_range is not None:
        values = stream_range.split('..')
        if len(values) == 2:
            return values
    return [None, None]


def to_array_filter(arg: str) -> typing.Iterable[str]:
    if arg is None:
        return None
    
    return json.loads(urllib.parse.unquote(arg))


def to_json(df: pd.DataFrame, col: str = None):
    if col is not None:
        index_col = col + '__index'
        df[index_col] = df[col].copy()
        df = df.set_index(index_col)
        # Replace NaN with pd.NA before converting to JSON to properly serialize as null
        return json.loads(df.fillna(value=pd.NA).to_json(orient="index"))
    
    # Replace NaN with pd.NA before converting to JSON to properly serialize as null
    return json.loads(df.fillna(value=pd.NA).to_json(orient="records"))