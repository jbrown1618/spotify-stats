import os
import pandas as pd

from utils.util import file_name_friendly, md_link


def make_playlist_summary(output_dir: str, playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    lines = []

    playlist_name = playlist_full["playlist_name"].iloc[0]
    lines.append(f"# {playlist_name}")
    lines.append("")

    display_tracks = playlist_full.copy()
    display_tracks["Artists"] = display_tracks["track_uri"].apply(lambda track_uri: get_display_artists(track_uri, track_artist_full, output_dir))
    table = display_tracks.to_markdown(index=False)

    lines.append(table)

    playlists_dir = os.path.join(output_dir, "playlists")
    if not os.path.isdir(playlists_dir):
        os.makedirs(playlists_dir)

    with open(f"{playlists_dir}/{file_name_friendly(playlist_name)}.md", "w") as f:
        f.write("\n".join(lines))


def get_display_artists(track_uri: str, track_artist_full: pd.DataFrame, output_dir: str):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri]
    artist_links = [get_artist_link(artist, output_dir) for i, artist in artists.iterrows()]
    return ", ".join(artist_links)


def get_artist_link(artist, output_dir: str):
    return md_link(artist["artist_name"], os.path.join(output_dir, "artists", file_name_friendly(artist["artist_name"]) + ".md"))
