import os
import pandas as pd

from utils.util import file_name_friendly, md_link


def make_playlist_summary(output_dir: str, playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    lines = []

    playlist_name = playlist_full["playlist_name"].iloc[0]
    lines.append(f"# {playlist_name}")
    lines.append("")
    lines += make_tracks_section(output_dir, playlist_full, track_artist_full)

    playlists_dir = os.path.join(output_dir, "playlists")
    if not os.path.isdir(playlists_dir):
        os.makedirs(playlists_dir)

    with open(f"{playlists_dir}/{file_name_friendly(playlist_name)}.md", "w") as f:
        f.write("\n".join(lines))


def make_tracks_section(output_dir: str, playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = playlist_full.copy()
    display_tracks["artist_names_sorting"] = display_tracks["track_uri"].apply(lambda track_uri: get_artist_names(track_uri, track_artist_full))
    display_tracks["Artists"] = display_tracks["track_uri"].apply(lambda track_uri: get_display_artists(track_uri, track_artist_full, output_dir))
    display_tracks["Track"] = display_tracks["track_name"]
    display_tracks["Album"] = display_tracks["album_name"]
    display_tracks = display_tracks.sort_values(by=["artist_names_sorting", "Album", "Track"])
    display_tracks = display_tracks[["Track", "Album", "Artists"]]
    table = display_tracks.to_markdown(index=False)
    return ["## Tracks", "", table]


def get_artist_names(track_uri: str, track_artist_full: pd.DataFrame):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri]
    names = [artist["artist_name"].lower() for i, artist in artists.iterrows()]
    return ", ".join(names)


def get_display_artists(track_uri: str, track_artist_full: pd.DataFrame, output_dir: str):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri]
    artist_links = [get_artist_link(artist, output_dir) for i, artist in artists.iterrows()]
    return ", ".join(artist_links)


def get_artist_link(artist, output_dir: str):
    if artist["artist_has_page"]:
        return md_link(artist["artist_name"], os.path.join(output_dir, "artists", file_name_friendly(artist["artist_name"]) + ".md"))
    else:
        return artist["artist_name"]
