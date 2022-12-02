import pandas as pd

from summarize.figures.albums_bar_chart import albums_bar_chart
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.labels_bar_chart import labels_bar_chart
from summarize.tables.albums_table import albums_table
from summarize.tables.artists_table import artists_table
from summarize.tables.labels_table import labels_table
from summarize.tables.tracks_table import tracks_table
from utils.audio_features import comparison_scatter_plot, top_and_bottom_lists
from utils.path import genre_album_graph_path, genre_artist_comparison_scatterplot_path, genre_artist_graph_path, genre_label_graph_path, genre_path, genre_tracks_path, genres_path
from utils.util import md_link, md_summary_details


def make_genre_summary(tracks: pd.DataFrame, track_artist_full: pd.DataFrame, album_record_label: pd.DataFrame):
    genre_name = tracks["genre"].iloc[0]
    print(f"Generating summary for genre {genre_name}")
    
    content = []
    content += title(genre_name)
    content += [md_link(f"{len(tracks)} songs", genre_tracks_path(genre_name, genres_path())), ""]
    content += artists_section(genre_name, tracks, track_artist_full)
    content += albums_section(genre_name, tracks)
    content += labels_section(genre_name, tracks, album_record_label)
    content += audio_features_section(tracks)

    tracks_content = tracks_section(genre_name, tracks, track_artist_full)

    with open(genre_path(genre_name), "w") as f:
        f.write("\n".join(content))

    with open(genre_tracks_path(genre_name), "w") as f:
        f.write("\n".join(tracks_content))


def title(genre_name):
    return [f"# {genre_name}", ""]


def artists_section(genre_name, tracks: pd.DataFrame, track_artist_full: pd.DataFrame):
    img = artists_bar_chart(tracks, track_artist_full, genre_artist_graph_path(genre_name), genre_artist_graph_path(genre_name, genres_path()))
    table_data = artists_table(tracks, track_artist_full, genres_path())

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    scatterplot = comparison_scatter_plot(
        tracks, 
        tracks["track_uri"].apply(lambda uri: primary_artist_name(uri, track_artist_full)), 
        "Artist", 
        genre_artist_comparison_scatterplot_path(genre_name), 
        genre_artist_comparison_scatterplot_path(genre_name, genres_path())
    )

    return ["## Top Artists", "", img, "", scatterplot , "", full_list]


def primary_artist_name(track_uri: str, track_artist_full: pd.DataFrame):
    name = track_artist_full[(track_artist_full["track_uri"] == track_uri) & (track_artist_full["artist_index"] == 0)].iloc[0]["artist_name"]
    return name


def albums_section(genre_name, tracks: pd.DataFrame):
    img = albums_bar_chart(tracks, genre_album_graph_path(genre_name), genre_album_graph_path(genre_name, genres_path()))
    table_data = albums_table(tracks)

    summary = f"See all {len(table_data)} albums"
    if len(table_data) > 100:
        summary = "See top 100 albums"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Top Albums", "", img, "", full_list, ""]


def labels_section(genre_name, tracks: pd.DataFrame, album_record_label: pd.DataFrame):
    img = labels_bar_chart(tracks, album_record_label, genre_label_graph_path(genre_name), genre_label_graph_path(genre_name, genres_path()))
    table_data = labels_table(tracks, album_record_label, genres_path())

    summary = f"See all {len(table_data)} labels"
    if len(table_data) > 100:
        summary = "See top 100 labels"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Top Record Labels", "", img, "", full_list, ""]


def tracks_section(genre_name: str, tracks: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = tracks_table(tracks, track_artist_full, genres_path())
    table = display_tracks.to_markdown(index=False)
    return [f"# Tracks in {genre_name}", "", table, ""]


def audio_features_section(tracks: pd.DataFrame):
    return ["## Audio Features", ""] + top_and_bottom_lists(tracks)
