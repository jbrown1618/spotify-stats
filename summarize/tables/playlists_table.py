import pandas as pd
from utils.markdown import md_image, md_link
from utils.path import playlist_overview_path

from utils.util import spotify_link

def playlists_table(playlists: pd.DataFrame, playlist_track: pd.DataFrame, tracks_full: pd.DataFrame, relative_to: str):
    playlist_display_data = pd.merge(playlists, playlist_track, on="playlist_uri")
    playlist_display_data = pd.merge(playlist_display_data, tracks_full, on="track_uri")
    track_counts = playlist_display_data\
        .groupby("playlist_uri")\
        .agg({"track_uri": "count", "track_liked": "sum"})\
        .reset_index()

    display_playlists = pd\
        .merge(left=playlists, right=track_counts, left_on="playlist_uri", right_on="playlist_uri", how="inner")

    display_playlists["🔗"] = display_playlists["playlist_uri"].apply(lambda uri: spotify_link(uri))
    display_playlists["Name"] = display_playlists["playlist_name"].apply(lambda name: md_link(name, playlist_overview_path(name, relative_to)))
    display_playlists["Tracks"] = display_playlists["track_uri"]
    display_playlists['💚'] = display_playlists["track_liked"]

    display_playlists["Art"] = display_playlists["playlist_image_url"].apply(lambda src: md_image("", src, 50))

    display_playlists = display_playlists[["Art", "Name", "Tracks", '💚', "🔗"]]

    display_playlists.sort_values(by=['💚', "Tracks", "Name"], ascending=False, inplace=True)

    liked_tracks_row = pd.DataFrame({
        'Art': '💚',
        'Name': md_link("Liked Tracks", playlist_overview_path('Liked Tracks', relative_to)),
        'Tracks': tracks_full['track_liked'].sum(),
        '💚': tracks_full['track_liked'].sum(),
        '🔗': ''
    }, index=[0])

    display_playlists = pd.concat([liked_tracks_row, display_playlists])

    return display_playlists