import pandas as pd
from data.provider import DataProvider
from utils.markdown import md_image

from utils.util import spotify_link
from utils.artist import get_display_artist

def artists_table(tracks: pd.DataFrame, relative_to: str):
    artist_data = DataProvider().track_counts_by_artist(tracks['track_uri'])

    artist_data = artist_data.sort_values(by=["track_liked", "track_uri", "artist_uri"], ascending=False)
    artist_data = artist_data.rename(columns={"track_uri": "Tracks", "track_liked": "💚", "artist_name": "Artist"})

    table_data = artist_data
    table_data["Artist"] = table_data["artist_uri"].apply(lambda uri: get_display_artist(uri, relative_to))
    table_data["Art"] = table_data["artist_image_url"].apply(lambda src: md_image("", src, 50))
    table_data["🔗"] = table_data["artist_uri"].apply(lambda uri: spotify_link(uri))
    table_data = table_data[["Art", "Tracks", "💚", "Artist", "🔗"]]

    return table_data
