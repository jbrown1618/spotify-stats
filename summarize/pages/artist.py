import pandas as pd
from summarize.tables.albums_table import albums_table

from summarize.tables.labels_table import labels_table
from summarize.tables.tracks_table import tracks_table
from utils.path import artist_path, artists_path, playlist_path
from utils.util import md_image, md_link

def make_artist_summary(artist: pd.Series, tracks: pd.DataFrame, track_artist_full: pd.DataFrame, album_record_label: pd.DataFrame, playlists: pd.DataFrame):
    print(f"Generating summary for artist {artist['artist_name']}")
    file_name = artist_path(artist["artist_name"])
    lines = []

    lines += title(artist)
    lines += image(artist)
    lines += playlists_section(playlists)
    lines += albums_section(tracks)
    lines += labels_section(tracks, album_record_label)
    lines += tracks_section(tracks, track_artist_full)

    with open(file_name, "w") as f:
        f.write("\n".join(lines))


def title(artist):
    return ["", f"# {artist['artist_name']}", ""]


def image(artist):
    return ["", md_image(artist["artist_name"], artist["artist_image_url"], 100), ""]


def playlists_section(playlists: pd.DataFrame):
    display_playlists = playlists.sort_values(by="playlist_artist_track_count", ascending=False)
    display_playlists["Art"] = display_playlists["playlist_image_url"].apply(lambda href: md_image("", href, 50))
    display_playlists["Playlist"] = display_playlists["playlist_uri"].apply(lambda uri: display_playlist(uri, playlists))
    display_playlists["Number of Tracks"] = display_playlists["playlist_artist_track_count"]
    display_playlists = display_playlists[["Number of Tracks", "Art", "Playlist"]]

    return [
        '## Featured on Playlists',
        display_playlists.to_markdown(index=False)
    ]


def albums_section(artist_tracks: pd.DataFrame):
    table_data = albums_table(artist_tracks)
    return ["## Top Albums", "", table_data.to_markdown(index=False), ""]


def labels_section(artist_tracks: pd.DataFrame, album_record_label: pd.DataFrame):
    table_data = labels_table(artist_tracks, album_record_label, artists_path())
    return ["## Top Record Labels", "", table_data.to_markdown(index=False), ""]


def tracks_section(tracks: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = tracks_table(tracks, track_artist_full, artists_path())
    return ["## Tracks", "", display_tracks.to_markdown(index=False)]


def display_playlist(playlist_uri: str, playlists: pd.DataFrame):
    playlist = playlists[playlists["playlist_uri"] == playlist_uri].iloc[0]
    return md_link(playlist["playlist_name"], playlist_path(playlist["playlist_name"], artists_path()))
