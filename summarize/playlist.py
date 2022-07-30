import os
import pandas as pd
from utils.path import artist_path, playlist_path, playlists_path
from utils.util import md_link


def make_playlist_summary(playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    playlist_name = playlist_full["playlist_name"].iloc[0]
    
    lines = []
    lines.append(f"# {playlist_name}")
    lines.append("")
    lines += make_tracks_section(playlist_full, track_artist_full)

    if not os.path.isdir(playlists_path()):
        os.makedirs(playlists_path())

    with open(playlist_path(playlist_name), "w") as f:
        f.write("\n".join(lines))


def make_tracks_section(playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = playlist_full.copy()
    display_tracks["artist_names_sorting"] = display_tracks["track_uri"].apply(lambda track_uri: get_artist_names(track_uri, track_artist_full))
    display_tracks["Artists"] = display_tracks["track_uri"].apply(lambda track_uri: get_display_artists(track_uri, track_artist_full))
    display_tracks["Track"] = display_tracks["track_name"]
    display_tracks["Album"] = display_tracks["album_name"]
    display_tracks["Liked"] = display_tracks["track_liked"]
    display_tracks = display_tracks.sort_values(by=["artist_names_sorting", "Album", "Track"])
    display_tracks = display_tracks[["Track", "Album", "Artists", "Liked"]]
    table = display_tracks.to_markdown(index=False)
    return ["## Tracks", "", table]


def get_artist_names(track_uri: str, track_artist_full: pd.DataFrame):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri]
    names = [artist["artist_name"].lower() for i, artist in artists.iterrows()]
    return ", ".join(names)


def get_display_artists(track_uri: str, track_artist_full: pd.DataFrame):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri]
    artist_links = [get_artist_link(artist) for i, artist in artists.iterrows()]
    return ", ".join(artist_links)


def get_artist_link(artist):
    if artist["artist_has_page"]:
        return md_link(artist["artist_name"], artist_path(artist["artist_name"], playlists_path()))
    else:
        return artist["artist_name"]
