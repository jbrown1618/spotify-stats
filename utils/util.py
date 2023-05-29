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


def first(series: pd.Series):
    return None if len(series) == 0 else series.iloc[0]
