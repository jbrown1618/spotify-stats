import pandas as pd

from utils.artist import get_display_artists, get_primary_artist_name
from utils.markdown import md_image
from utils.record_label import get_display_labels
from utils.util import spotify_link

def tracks_table(tracks: pd.DataFrame, track_artist_full: pd.DataFrame, relative_to: str):
    table_data = tracks.copy()
    table_data["artist_names_sorting"] = table_data["track_uri"].apply(lambda track_uri: get_primary_artist_name(track_uri, track_artist_full))
    table_data["Art"] = table_data["album_image_url"].apply(lambda src: md_image("", src, 50))
    table_data["Artists"] = table_data["track_uri"].apply(lambda track_uri: get_display_artists(track_uri, track_artist_full, relative_to))
    table_data["Track"] = table_data["track_name"]
    table_data["🔗"] = table_data["track_uri"].apply(lambda uri: spotify_link(uri))
    table_data["Album"] = table_data["album_name"]
    table_data["Label"] = table_data["album_label"].apply(lambda label: get_display_labels(label, relative_to))
    table_data["💚"] = table_data["track_liked"].apply(lambda liked: "💚" if liked else "")
    table_data = table_data.sort_values(by=["artist_names_sorting", "album_release_date", "Album", "Track"])
    table_data = table_data[["Art", "Track", "Album", "Artists", "Label", "💚", "🔗"]]
    
    return table_data
