import re
import pandas as pd

from utils.markdown import md_link


def get_id(uri: str):
    last_colon = uri.rindex(":") + 1
    return uri[last_colon:]


def spotify_link(uri: str):
    pieces = uri.split(":")
    type = pieces[1]
    id = pieces[2]
    return md_link("🔗", f"https://open.spotify.com/{type}/{id}")


def file_name_friendly(text: str):
    return re.sub(r"[^a-z0-9]", "_", text.lower())


def prefix_df(df: pd.DataFrame, prefix: str, prefixes: list[str]):
    df.columns = [prefix_col(col, prefix, prefixes) for col in df.columns]


def prefix_col(col: str, prefix: str, prefixes: list[str]):
    for other_prefix in prefixes:
        if col.startswith(other_prefix):
            return col
    return prefix + col


def first(series: pd.Series):
    return None if len(series) == 0 else series.iloc[0]
