import math
from datetime import datetime
import pandas as pd
from utils.markdown import empty_header, md_table, md_image

from utils.util import first

def today():
    return datetime.today()

def this_year():
    return today().strftime('%Y')

def this_date():
    return today().strftime('%Y-%m-%d')

def release_year(release_date:str):
    first_four = release_date[0:4]
    return first_four if first_four.isnumeric() else None


def newest_and_oldest_albums(tracks: pd.DataFrame):
    albums = tracks.groupby("album_uri").agg({"track_uri": "count", "album_name": first, "album_image_url": first, "album_release_date": first}).reset_index()
    top_count = math.ceil(min(10, albums.size / 2))

    newest_albums = albums.sort_values(by='album_release_date', ascending=False)\
        .head(top_count)\
        .reset_index()

    oldest_albums = albums.sort_values(by='album_release_date', ascending=True)\
        .head(top_count)\
        .reset_index()


    data = pd.DataFrame({
        empty_header(1): newest_albums.apply(album_image, axis=1),
        f"{top_count} newest albums": newest_albums.apply(album_row, axis=1),
        empty_header(2): oldest_albums.apply(album_image, axis=1),
        f"{top_count} oldest albums": oldest_albums.apply(album_row, axis=1)
    })
    
    return md_table(data)


def album_row(row: pd.Series):
    return f'{row["album_name"]} ({row["album_release_date"]})'


def album_image(row: pd.Series):
    return md_image(row["album_name"], row["album_image_url"], 50)