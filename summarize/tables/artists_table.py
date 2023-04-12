import pandas as pd
from utils.markdown import md_image

from utils.util import first, spotify_link
from utils.artist import get_display_artist

def artists_table(tracks: pd.DataFrame, track_artist_full: pd.DataFrame, relative_to: str):
    joined = pd.merge(track_artist_full, tracks, on="track_uri")
    grouped = joined.groupby("artist_uri").agg({"track_uri": "count", "track_liked": "sum", "artist_name": first, "artist_image_url": first}).reset_index()
    grouped = grouped.sort_values(by=["track_liked", "track_uri", "artist_uri"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Tracks", "track_liked": "💚", "artist_name": "Artist"})

    table_data = grouped
    table_data["Artist"] = table_data["artist_uri"].apply(lambda uri: get_display_artist(uri, track_artist_full, relative_to))
    table_data["Art"] = table_data["artist_image_url"].apply(lambda src: md_image("", src, 50))
    table_data["🔗"] = table_data["artist_uri"].apply(lambda uri: spotify_link(uri))
    table_data = table_data[["Art", "Tracks", "💚", "Artist", "🔗"]]

    return table_data
