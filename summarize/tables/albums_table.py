import pandas as pd

from utils.markdown import md_image
from utils.util import spotify_link, first

def albums_table(tracks: pd.DataFrame):
    grouped = tracks.groupby("album_uri").agg({
        "track_uri": "count", 
        "track_liked": "sum", 
        "album_name": first, 
        "album_image_url": first, 
        "album_release_date": first, 
        "album_rank": first
    }).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "track_liked", "album_name"], ascending=False)
    grouped = grouped.rename(columns={
        "track_uri": "Tracks", 
        "track_liked": "💚", 
        "album_name": "Album", 
        "album_release_date": 
        "Release Date", 
        "album_rank": "Rank"
    })

    grouped["Art"] = grouped["album_image_url"].apply(lambda src: md_image("", src, 50))
    grouped["🔗"] = grouped["album_uri"].apply(lambda uri: spotify_link(uri))
    table_data = grouped[["Art", "Rank", "Tracks", "💚", "Album", "Release Date", "🔗"]]

    return table_data
