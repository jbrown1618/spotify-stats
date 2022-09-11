import pandas as pd
from utils.path import playlist_path, readme_path
from utils.settings import output_dir
from utils.util import md_link, spotify_link

def make_readme(playlists: pd.DataFrame, playlist_track: pd.DataFrame):
    print("Generating Overview")

    readme = []

    readme += title("jbrown1618")
    readme += byline()
    readme += liked_songs()
    readme += playlists_section(playlists, playlist_track)

    with open(readme_path(), "w") as f:
        f.write("\n".join(readme))


def title(user: str):
    return [f"# Spotify Summary for {user}", ""]


def byline():
    return [f"Generated by {md_link('jbrown1618/spotify-stats', 'https://github.com/jbrown1618/spotify-stats')}", ""]


def liked_songs():
    return ["## Liked Songs", md_link("Liked Songs", playlist_path("Liked Songs", output_dir()))]


def playlists_section(playlists: pd.DataFrame, playlist_track: pd.DataFrame):
    track_counts = pd\
        .merge(left=playlists, right=playlist_track, left_on="playlist_uri", right_on="playlist_uri", how="inner")\
        .groupby("playlist_uri")["track_uri"]\
        .count()

    display_playlists = pd\
        .merge(left=playlists, right=track_counts, left_on="playlist_uri", right_on="playlist_uri", how="inner")

    display_playlists["🔗"] = display_playlists["playlist_uri"].apply(lambda uri: spotify_link(uri))
    display_playlists["Name"] = display_playlists["playlist_name"].apply(lambda name: md_link(name, playlist_path(name, output_dir())))
    display_playlists["Number of Songs"] = display_playlists["track_uri"]

    display_playlists = display_playlists[["Name", "Number of Songs", "🔗"]]

    display_playlists.sort_values(by="Name", inplace=True)

    table = display_playlists.to_markdown(index=False)

    return ["## Playlists", "", table, ""]
