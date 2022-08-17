import os
import pandas as pd
from utils.path import artist_path, artists_path

def make_artist_summary(artist: pd.Series, tracks: pd.DataFrame):
    print(f"Generating summary for artist {artist['artist_name']}")
    file_name = artist_path(artist["artist_name"])
    lines = []

    lines.append(f"# {artist['artist_name']}")
    lines.append("")
    lines += make_tracks_section(tracks)

    with open(file_name, "w") as f:
        f.write("\n".join(lines))


def make_tracks_section(tracks: pd.DataFrame):
    display_tracks = tracks.copy()

    display_tracks["Track"] = display_tracks["track_name"]
    display_tracks["Album"] = display_tracks["album_name"]
    display_tracks["Liked"] = display_tracks["track_liked"]
    display_tracks.sort_values(by=["album_release_date", "Track"], inplace=True)
    display_tracks = display_tracks[["Track", "Album", "Liked"]]

    table = display_tracks.to_markdown(index=False)

    return ["## Tracks", "", table]