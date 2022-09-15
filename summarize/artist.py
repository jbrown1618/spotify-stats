import pandas as pd

from utils.path import artist_path
from utils.util import first, md_image, spotify_link

def make_artist_summary(artist: pd.Series, tracks: pd.DataFrame, album_record_label: pd.DataFrame):
    print(f"Generating summary for artist {artist['artist_name']}")
    file_name = artist_path(artist["artist_name"])
    lines = []

    lines += title(artist)
    lines += image(artist)
    lines += albums_section(tracks)
    lines += labels_section(tracks, album_record_label)
    lines += tracks_section(tracks)

    with open(file_name, "w") as f:
        f.write("\n".join(lines))


def title(artist):
    return ["", f"# {artist['artist_name']}", ""]


def image(artist):
    return ["", md_image(artist["artist_name"], artist["artist_image_url"], 100), ""]


def albums_section(artist_tracks: pd.DataFrame):
    grouped = artist_tracks.groupby("album_uri").agg({"track_uri": "count", "album_name": first, "album_image_url": first}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "album_name"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "album_name": "Album"})

    grouped["Art"] = grouped["album_image_url"].apply(lambda src: md_image("", src, 50))
    table_data = grouped[["Number of Tracks", "Art", "Album"]]

    return ["## Top Albums", "", table_data.to_markdown(index=False), ""]


def labels_section(artist_tracks: pd.DataFrame, album_record_label: pd.DataFrame):
    grouped = pd.merge(artist_tracks, album_record_label, on="album_uri").groupby("album_standardized_label").agg({"track_uri": "count"}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "album_standardized_label"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "album_standardized_label": "Label"})

    table_data = grouped[["Number of Tracks", "Label"]]

    return ["## Top Record Labels", "", table_data.to_markdown(index=False), ""]


def tracks_section(tracks: pd.DataFrame):
    display_tracks = tracks.copy()

    display_tracks["Art"] = display_tracks["album_image_url"].apply(lambda src: md_image("", src, 50))
    display_tracks["Track"] = display_tracks["track_name"]
    display_tracks["🔗"] = display_tracks["track_uri"].apply(lambda uri: spotify_link(uri))
    display_tracks["Album"] = display_tracks["album_name"]
    display_tracks["Label"] = display_tracks["album_label"]
    display_tracks["💚"] = display_tracks["track_liked"].apply(lambda liked: "💚" if liked else "")
    display_tracks.sort_values(by=["album_release_date", "Track"], inplace=True)
    display_tracks = display_tracks[["Art", "Track", "Album", "Label", "💚", "🔗"]]

    table = display_tracks.to_markdown(index=False)

    return ["## Tracks", "", table]