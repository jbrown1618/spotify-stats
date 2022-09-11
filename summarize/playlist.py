import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.path import artist_path, playlist_album_graph_path, playlist_label_graph_path, playlist_path, playlists_path, playlist_artist_graph_path
from utils.util import first, md_image, md_link, md_summary_details, spotify_link


def make_playlist_summary(playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame, is_liked_songs=False):
    playlist_name = "Liked Songs" if is_liked_songs else playlist_full["playlist_name"].iloc[0]
    playlist_image_url = None if is_liked_songs else playlist_full["playlist_image_url"].iloc[0]
    print(f"Generating summary for playlist {playlist_name}")
    
    lines = []
    lines += title(playlist_name)
    lines += image(playlist_name, playlist_image_url)
    lines += [f"{len(playlist_full)} songs", ""]
    lines += artists_section(playlist_name, playlist_full, track_artist_full)
    lines += albums_section(playlist_name, playlist_full)
    lines += labels_section(playlist_name, playlist_full)
    lines += tracks_section(playlist_full, track_artist_full)

    with open(playlist_path(playlist_name), "w") as f:
        f.write("\n".join(lines))


def title(playlist_name):
    return [f"# {playlist_name}", ""]


def image(playlist_name, playlist_image_url):
    if playlist_image_url is None:
        return []
        
    return ["", md_image(playlist_name, playlist_image_url, 100), ""]


def artists_section(playlist_name, playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    joined = pd.merge(track_artist_full, playlist_full, on="track_uri")
    grouped = joined.groupby("artist_uri").agg({"track_uri": "count", "artist_name": first, "artist_image_url": first}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "artist_uri"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "artist_name": "Artist"})
    
    fig_data = grouped[["Number of Tracks", "Artist"]].head(30)
    sns.set(rc = {"figure.figsize": (13,13) })
    ax = sns.barplot(data=fig_data, x="Number of Tracks", y="Artist")
    ax.bar_label(ax.containers[0])
    ax.get_figure().savefig(playlist_artist_graph_path(playlist_name))
    img = md_image(
        f"Bar chart of top {len(fig_data)} artists in {playlist_name}", 
        playlist_artist_graph_path(playlist_name, playlists_path())
    )
    plt.clf()

    table_data = grouped
    table_data["Artist"] = table_data["artist_uri"].apply(lambda uri: get_display_artist(uri, track_artist_full))
    table_data["Art"] = table_data["artist_image_url"].apply(lambda src: md_image("", src, 50))
    table_data["🔗"] = table_data["artist_uri"].apply(lambda uri: spotify_link(uri))
    table_data = table_data[["Number of Tracks", "Art", "Artist", "🔗"]]

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Top Artists", "", img, "", full_list, ""]


def albums_section(playlist_name, playlist_full: pd.DataFrame):
    grouped = playlist_full.groupby("album_uri").agg({"track_uri": "count", "album_name": first, "album_image_url": first}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "album_name"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "album_name": "Album"})
    
    fig_data = grouped[["Number of Tracks", "Album"]].head(30)
    sns.set(rc = {"figure.figsize": (13,13) })
    ax = sns.barplot(data=fig_data, x="Number of Tracks", y="Album")
    ax.bar_label(ax.containers[0])
    ax.get_figure().savefig(playlist_album_graph_path(playlist_name))
    img = md_image(
        f"Bar chart of top {len(fig_data)} albums in {playlist_name}", 
        playlist_album_graph_path(playlist_name, playlists_path())
    )
    plt.clf()

    grouped["Art"] = grouped["album_image_url"].apply(lambda src: md_image("", src, 50))
    grouped["🔗"] = grouped["album_uri"].apply(lambda uri: spotify_link(uri))
    table_data = grouped[["Number of Tracks", "Art", "Album", "🔗"]]

    summary = f"See all {len(table_data)} albums"
    if len(table_data) > 100:
        summary = "See top 100 albums"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Top Albums", "", img, "", full_list, ""]


def labels_section(playlist_name, playlist_full: pd.DataFrame):
    grouped = playlist_full.groupby("album_label").agg({"track_uri": "count"}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "album_label"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "album_label": "Label"})
    
    fig_data = grouped[["Number of Tracks", "Label"]].head(30)
    sns.set(rc = {"figure.figsize": (13,13) })
    ax = sns.barplot(data=fig_data, x="Number of Tracks", y="Label")
    ax.bar_label(ax.containers[0])
    ax.get_figure().savefig(playlist_label_graph_path(playlist_name))
    img = md_image(
        f"Bar chart of top {len(fig_data)} record labels in {playlist_name}", 
        playlist_label_graph_path(playlist_name, playlists_path())
    )
    plt.clf()

    table_data = grouped[["Number of Tracks", "Label"]]

    summary = f"See all {len(table_data)} labels"
    if len(table_data) > 100:
        summary = "See top 100 labels"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Top Record Labels", "", img, "", full_list, ""]


def tracks_section(playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = playlist_full.copy()
    display_tracks["artist_names_sorting"] = display_tracks["track_uri"].apply(lambda track_uri: get_artist_names(track_uri, track_artist_full))
    display_tracks["Art"] = display_tracks["album_image_url"].apply(lambda src: md_image("", src, 50))
    display_tracks["Artists"] = display_tracks["track_uri"].apply(lambda track_uri: get_display_artists(track_uri, track_artist_full))
    display_tracks["Track"] = display_tracks["track_name"]
    display_tracks["🔗"] = display_tracks["track_uri"].apply(lambda uri: spotify_link(uri))
    display_tracks["Album"] = display_tracks["album_name"]
    display_tracks["Label"] = display_tracks["album_label"]
    display_tracks["💚"] = display_tracks["track_liked"].apply(lambda liked: "💚" if liked else "")
    display_tracks = display_tracks.sort_values(by=["artist_names_sorting", "album_release_date", "Album", "Track"])
    display_tracks = display_tracks[["Art", "Track", "Album", "Artists", "Label", "💚", "🔗"]]
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


def get_display_artist(artist_uri: str, track_artist_full: pd.DataFrame):
    artist = track_artist_full[track_artist_full["artist_uri"] == artist_uri].iloc[0]
    return get_artist_link(artist)


def get_artist_link(artist):
    if artist["artist_has_page"]:
        return md_link(artist["artist_name"], artist_path(artist["artist_name"], playlists_path()))
    else:
        return artist["artist_name"]

