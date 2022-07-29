import os
import pandas as pd

from utils.util import file_name_friendly


def make_artist_summary(output_dir, artist: pd.Series, tracks: pd.DataFrame):
    lines = []

    lines.append(f"# {artist['artist_name']}")
    lines.append("")
    lines += make_tracks_section(tracks)

    artists_dir = os.path.join(output_dir, "artists")
    if not os.path.isdir(artists_dir):
        os.makedirs(artists_dir)

    file_name = os.path.join(artists_dir, file_name_friendly(artist['artist_name']) + ".md")
    with open(file_name, "w") as f:
        f.write("\n".join(lines))


def make_tracks_section(tracks: pd.DataFrame):
    display_tracks = tracks.copy()

    display_tracks["Track"] = display_tracks["track_name"]
    display_tracks["Album"] = display_tracks["album_name"]
    display_tracks.sort_values(by=["album_release_date", "Track"], inplace=True)
    display_tracks = display_tracks[["Track", "Album"]]

    table = display_tracks.to_markdown(index=False)

    return ["## Tracks", "", table]