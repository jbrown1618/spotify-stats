import pandas as pd

from summarize.figures.albums_bar_chart import albums_bar_chart
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.genres_bar_chart import genres_bar_chart
from summarize.figures.labels_bar_chart import labels_bar_chart
from summarize.tables.albums_table import albums_table
from summarize.tables.artists_table import artists_table
from summarize.tables.genres_table import genres_table
from summarize.tables.labels_table import labels_table
from summarize.tables.tracks_table import tracks_table
from utils.audio_features import comparison_scatter_plot, top_and_bottom_lists
from utils.path import playlist_album_graph_path, playlist_genre_graph_path, playlist_label_graph_path, playlist_overview_path, playlist_path, playlist_tracks_path, playlist_artist_comparison_scatterplot_path, playlist_artist_graph_path
from utils.util import md_image, md_link, md_summary_details


def make_playlist_summary(playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame, album_record_label: pd.DataFrame, track_genre: pd.DataFrame, is_liked_songs=False):
    playlist_name = "Liked Songs" if is_liked_songs else playlist_full["playlist_name"].iloc[0]
    playlist_image_url = None if is_liked_songs else playlist_full["playlist_image_url"].iloc[0]
    print(f"Generating summary for playlist {playlist_name}")
    
    content = []
    content += title(playlist_name)
    content += image(playlist_name, playlist_image_url)
    content += [md_link(f"{len(playlist_full)} songs", playlist_tracks_path(playlist_name, playlist_path(playlist_name))), ""]
    content += artists_section(playlist_name, playlist_full, track_artist_full)
    content += albums_section(playlist_name, playlist_full)
    content += labels_section(playlist_name, playlist_full, album_record_label)
    content += genres_section(playlist_name, playlist_full, track_genre)
    content += audio_features_section(playlist_full)

    tracks_content = tracks_section(playlist_name, playlist_full, track_artist_full)

    with open(playlist_overview_path(playlist_name), "w") as f:
        f.write("\n".join(content))

    with open(playlist_tracks_path(playlist_name), "w") as f:
        f.write("\n".join(tracks_content))


def title(playlist_name):
    return [f"# {playlist_name}", ""]


def image(playlist_name, playlist_image_url):
    if playlist_image_url is None:
        return []
        
    return ["", md_image(playlist_name, playlist_image_url, 100), ""]


def artists_section(playlist_name, playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    img = artists_bar_chart(playlist_full, track_artist_full, playlist_artist_graph_path(playlist_name), playlist_artist_graph_path(playlist_name, playlist_path(playlist_name)))
    table_data = artists_table(playlist_full, track_artist_full, playlist_path(playlist_name))

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    scatterplot = comparison_scatter_plot(
        playlist_full, 
        playlist_full["track_uri"].apply(lambda uri: primary_artist_name(uri, track_artist_full)), 
        "Artist", 
        playlist_artist_comparison_scatterplot_path(playlist_name), 
        playlist_artist_comparison_scatterplot_path(playlist_name, playlist_path(playlist_name))
    )

    return ["## Top Artists", "", img, "", scatterplot , "", full_list, ""]


def primary_artist_name(track_uri: str, track_artist_full: pd.DataFrame):
    name = track_artist_full[(track_artist_full["track_uri"] == track_uri) & (track_artist_full["artist_index"] == 0)].iloc[0]["artist_name"]
    return name


def albums_section(playlist_name, playlist_full: pd.DataFrame):
    img = albums_bar_chart(playlist_full, playlist_album_graph_path(playlist_name), playlist_album_graph_path(playlist_name, playlist_path(playlist_name)))
    table_data = albums_table(playlist_full)

    summary = f"See all {len(table_data)} albums"
    if len(table_data) > 100:
        summary = "See top 100 albums"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Top Albums", "", img, "", full_list, ""]


def labels_section(playlist_name, playlist_full: pd.DataFrame, album_record_label: pd.DataFrame):
    img = labels_bar_chart(playlist_full, album_record_label, playlist_label_graph_path(playlist_name), playlist_label_graph_path(playlist_name, playlist_path(playlist_name)))
    table_data = labels_table(playlist_full, album_record_label, playlist_path(playlist_name))

    summary = f"See all {len(table_data)} labels"
    if len(table_data) > 100:
        summary = "See top 100 labels"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Top Record Labels", "", img, "", full_list, ""]


def genres_section(playlist_name: str, tracks: pd.DataFrame, track_genre: pd.DataFrame):
    img = genres_bar_chart(tracks, track_genre, playlist_genre_graph_path(playlist_name), playlist_genre_graph_path(playlist_name, playlist_path(playlist_name)))
    table_data = genres_table(tracks, track_genre, playlist_path(playlist_name))
    
    summary = f"See all {len(table_data)} genres"
    if len(table_data) > 100:
        summary = "See top 100 genres"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Genres", "", img, "", full_list, ""]


def tracks_section(playlist_name: str, playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = tracks_table(playlist_full, track_artist_full, playlist_path(playlist_name))
    table = display_tracks.to_markdown(index=False)
    return [f"# Tracks in {playlist_name}", "", table, ""]


def audio_features_section(playlist_full: pd.DataFrame):
    return ["## Audio Features", ""] + top_and_bottom_lists(playlist_full)
