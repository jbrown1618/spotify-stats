import pandas as pd
from utils.util import md_image, spotify_link, first

def albums_table(tracks: pd.DataFrame):
    grouped = tracks.groupby("album_uri").agg({"track_uri": "count", "album_name": first, "album_image_url": first}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "album_name"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "album_name": "Album"})

    grouped["Art"] = grouped["album_image_url"].apply(lambda src: md_image("", src, 50))
    grouped["🔗"] = grouped["album_uri"].apply(lambda uri: spotify_link(uri))
    table_data = grouped[["Number of Tracks", "Art", "Album", "🔗"]]

    return table_data