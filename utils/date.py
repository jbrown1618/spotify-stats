import math
import pandas as pd
from utils.markdown import md_table, md_image

from utils.util import first

def release_year(release_date:str):
    first_four = release_date[0:4]
    return first_four if first_four.isnumeric() else None


def newest_and_oldest_albums(tracks: pd.DataFrame):
    albums = tracks.groupby("album_uri").agg({"track_uri": "count", "album_name": first, "album_image_url": first, "album_release_date": first}).reset_index()
    top_count = math.ceil(min(10, albums.size / 2))

    newest_albums = albums.sort_values(by='album_release_date', ascending=False)\
        .head(top_count)\
        .reset_index()\
        .apply(album_row, axis=1)

    oldest_albums = albums.sort_values(by='album_release_date', ascending=True)\
        .head(top_count)\
        .reset_index()\
        .apply(album_row, axis=1)

    data = pd.DataFrame({
        f"{top_count} newest albums": newest_albums,
        f"{top_count} oldest albums": oldest_albums
    })
    
    return md_table(data)


def album_row(row: pd.Series):
    return f'<div style="display:flex; align-items:center;">{md_image(row["album_name"], row["album_image_url"], 50)} <span style="padding-left:10px;">{row["album_name"]} ({row["album_release_date"]})</span></div>'