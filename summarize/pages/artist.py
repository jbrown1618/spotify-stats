import pandas as pd
from summarize.tables.albums_table import albums_table

from summarize.tables.labels_table import labels_table
from summarize.tables.tracks_table import tracks_table
from utils.path import artist_path, artists_path
from utils.util import md_image

def make_artist_summary(artist: pd.Series, tracks: pd.DataFrame, track_artist_full: pd.DataFrame, album_record_label: pd.DataFrame):
    print(f"Generating summary for artist {artist['artist_name']}")
    file_name = artist_path(artist["artist_name"])
    lines = []

    lines += title(artist)
    lines += image(artist)
    lines += albums_section(tracks)
    lines += labels_section(tracks, album_record_label)
    lines += tracks_section(tracks, track_artist_full)

    with open(file_name, "w") as f:
        f.write("\n".join(lines))


def title(artist):
    return ["", f"# {artist['artist_name']}", ""]


def image(artist):
    return ["", md_image(artist["artist_name"], artist["artist_image_url"], 100), ""]


def albums_section(artist_tracks: pd.DataFrame):
    table_data = albums_table(artist_tracks)
    return ["## Top Albums", "", table_data.to_markdown(index=False), ""]


def labels_section(artist_tracks: pd.DataFrame, album_record_label: pd.DataFrame):
    table_data = labels_table(artist_tracks, album_record_label, artists_path())
    return ["## Top Record Labels", "", table_data.to_markdown(index=False), ""]


def tracks_section(tracks: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = tracks_table(tracks, track_artist_full, artists_path())
    return ["## Tracks", "", display_tracks.to_markdown(index=False)]
