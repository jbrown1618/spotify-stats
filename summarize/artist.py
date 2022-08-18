import pandas as pd
from utils.path import artist_path
from utils.util import md_image

def make_artist_summary(artist: pd.Series, tracks: pd.DataFrame):
    print(f"Generating summary for artist {artist['artist_name']}")
    file_name = artist_path(artist["artist_name"])
    lines = []

    lines += title(artist)
    lines += image(artist)
    lines += tracks_section(tracks)

    with open(file_name, "w") as f:
        f.write("\n".join(lines))


def title(artist):
    return ["", f"# {artist['artist_name']}", ""]


def image(artist):
    return ["", md_image(artist["artist_name"], artist["artist_image_url"], 100), ""]


def tracks_section(tracks: pd.DataFrame):
    display_tracks = tracks.copy()

    display_tracks["Track"] = display_tracks["track_name"]
    display_tracks["Album"] = display_tracks["album_name"]
    display_tracks["Liked"] = display_tracks["track_liked"].apply(lambda liked: "💚" if liked else "")
    display_tracks.sort_values(by=["album_release_date", "Track"], inplace=True)
    display_tracks = display_tracks[["Track", "Album", "Liked"]]

    table = display_tracks.to_markdown(index=False)

    return ["## Tracks", "", table]