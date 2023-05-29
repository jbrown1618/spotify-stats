import pandas as pd
from data.provider import DataProvider

from utils.util import md_link
from utils.path import artist_overview_path

def get_primary_artist_name(track_uri: str):
    return DataProvider().primary_artist(track_uri)['artist_name'].upper()


def get_display_artists(track_uri: str, relative_to: str):
    artists = DataProvider().artists(track_uri=track_uri)
    artist_links = [get_artist_link(artist, relative_to) for i, artist in artists.iterrows()]
    return ", ".join(artist_links)


def get_display_artist(artist_uri: str, relative_to: str):
    artist = DataProvider().artist(artist_uri)
    return get_artist_link(artist, relative_to)


def get_artist_link(artist: pd.Series, relative_to: str, suffix: str = ''):
    if pd.isna(artist["artist_name" + suffix]):
        return ""
    
    if artist["artist_has_page" + suffix]:
        return md_link(artist["artist_name" + suffix], artist_overview_path(artist["artist_name" + suffix], relative_to))

    return artist["artist_name" + suffix]
