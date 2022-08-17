import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from utils.path import artist_path, playlist_path, playlists_path, playlist_artist_graph_path
from utils.util import md_image, md_link, md_summary_details


def make_playlist_summary(playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    playlist_name = playlist_full["playlist_name"].iloc[0]
    playlist_image_url = playlist_full["playlist_image_url"].iloc[0]
    print(f"Generating summary for playlist {playlist_name}")
    
    lines = []
    lines += title(playlist_name)
    lines += image(playlist_name, playlist_image_url)
    lines += artists_section(playlist_name, playlist_full, track_artist_full)
    lines += tracks_section(playlist_full, track_artist_full)

    with open(playlist_path(playlist_name), "w") as f:
        f.write("\n".join(lines))


def title(playlist_name):
    return [f"# {playlist_name}", ""]


def image(playlist_name, playlist_image_url):
    return ["", md_image(playlist_name, playlist_image_url, 100), ""]


def artists_section(playlist_name, playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    joined = pd.merge(track_artist_full, playlist_full, on="track_uri")
    grouped = joined.groupby("artist_uri").agg({"track_uri": "count", "artist_name": first}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "artist_uri"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "artist_name": "Artist"})
    grouped = grouped.drop(columns="artist_uri")
    
    fig_data = grouped.head(30)
    sns.set(rc = {"figure.figsize": (13,13) })
    ax = sns.barplot(data=fig_data, x="Number of Tracks", y="Artist")
    ax.bar_label(ax.containers[0])
    ax.get_figure().savefig(playlist_artist_graph_path(playlist_name))
    img = md_image(
        f"Bar chart of top {len(fig_data)} artists in {playlist_name}", 
        playlist_artist_graph_path(playlist_name, playlists_path())
    )
    plt.clf()

    full_list = md_summary_details("See all artists", grouped.to_markdown(index=False))

    return ["## Top Artists", "", img, "", full_list, ""]


def tracks_section(playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = playlist_full.copy()
    display_tracks["artist_names_sorting"] = display_tracks["track_uri"].apply(lambda track_uri: get_artist_names(track_uri, track_artist_full))
    display_tracks["Artists"] = display_tracks["track_uri"].apply(lambda track_uri: get_display_artists(track_uri, track_artist_full))
    display_tracks["Track"] = display_tracks["track_name"]
    display_tracks["Album"] = display_tracks["album_name"]
    display_tracks["Liked"] = display_tracks["track_liked"].apply(lambda liked: "💚" if liked else "")
    display_tracks = display_tracks.sort_values(by=["artist_names_sorting", "Album", "Track"])
    display_tracks = display_tracks[["Track", "Album", "Artists", "Liked"]]
    table = display_tracks.to_markdown(index=False)
    return ["## Tracks", "", table, ""]


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


def first(series: pd.Series):
    return None if len(series) == 0 else series.iloc[0]