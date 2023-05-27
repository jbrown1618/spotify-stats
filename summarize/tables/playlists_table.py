import pandas as pd
from data.provider import DataProvider
from utils.markdown import md_image, md_link
from utils.path import playlist_overview_path

from utils.util import spotify_link

def playlists_table(relative_to: str):
    dp = DataProvider()
    display_playlists = dp.playlists().copy()

    display_playlists["🔗"] = display_playlists["playlist_uri"].apply(lambda uri: spotify_link(uri))
    display_playlists["Name"] = display_playlists["playlist_name"].apply(lambda name: md_link(name, playlist_overview_path(name, relative_to)))
    display_playlists["Tracks"] = display_playlists["playlist_track_count"]
    display_playlists['💚'] = display_playlists["playlist_track_liked_count"]

    display_playlists["Art"] = display_playlists["playlist_image_url"].apply(lambda src: md_image("", src, 50))

    display_playlists = display_playlists[["Art", "Name", "Tracks", '💚', "🔗"]]

    display_playlists.sort_values(by=['💚', "Tracks", "Name"], ascending=False, inplace=True)

    liked_tracks_count = len(dp.tracks(liked=True))

    liked_tracks_row = pd.DataFrame({
        'Art': '💚',
        'Name': md_link("Liked Tracks", playlist_overview_path('Liked Tracks', relative_to)),
        'Tracks': liked_tracks_count,
        '💚': liked_tracks_count,
        '🔗': ''
    }, index=[0])

    display_playlists = pd.concat([liked_tracks_row, display_playlists])

    return display_playlists