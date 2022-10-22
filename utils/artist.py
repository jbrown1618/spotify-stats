import pandas as pd

from utils.util import md_link
from utils.path import artist_path

def get_primary_artist_name(track_uri: str, track_artist_full: pd.DataFrame):
    artists = track_artist_full[(track_artist_full["track_uri"] == track_uri) & (track_artist_full["artist_index"] == 0)]
    return artists["artist_name"].iloc[0].upper()


def get_display_artists(track_uri: str, track_artist_full: pd.DataFrame, relative_to: str):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri].sort_values(by="artist_index")
    artist_links = [get_artist_link(artist, relative_to) for i, artist in artists.iterrows()]
    return ", ".join(artist_links)


def get_display_artist(artist_uri: str, track_artist_full: pd.DataFrame, relative_to: str):
    artist = track_artist_full[track_artist_full["artist_uri"] == artist_uri].iloc[0]
    return get_artist_link(artist, relative_to)


def get_artist_link(artist: pd.Series, relative_to: str):
    if artist["artist_has_page"]:
        return md_link(artist["artist_name"], artist_path(artist["artist_name"], relative_to))
    else:
        return artist["artist_name"]
