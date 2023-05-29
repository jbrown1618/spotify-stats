import pandas as pd
from data.provider import DataProvider

from summarize.figures.albums_bar_chart import albums_bar_chart
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.labels_bar_chart import labels_bar_chart
from summarize.figures.years_bar_chart import years_bar_chart
from summarize.pages.audio_features import make_audio_features_page
from summarize.tables.albums_table import albums_table
from summarize.tables.artists_table import artists_table
from summarize.tables.labels_table import labels_table
from summarize.tables.tracks_table import tracks_table
from utils.audio_features import comparison_scatter_plot
from utils.date import newest_and_oldest_albums
from utils.markdown import md_table, md_link, md_truncated_table
from utils.path import genre_album_graph_path, genre_artist_comparison_scatterplot_path, genre_artist_graph_path, genre_audio_features_chart_path, genre_audio_features_path, genre_label_graph_path, genre_overview_path, genre_path, genre_tracks_path, genre_years_graph_path, genres_path


def make_genre_summary(genre_name: str, tracks: pd.DataFrame):
    print(f"Generating summary for genre {genre_name}")
    
    content = []
    content += title(genre_name)
    content += [md_link(f"{len(tracks)} songs", genre_tracks_path(genre_name, genre_path(genre_name))), ""]
    content += [md_link(f"See Audio Features", genre_audio_features_path(genre_name, genre_path(genre_name))), ""]
    content += artists_section(genre_name, tracks)
    content += albums_section(genre_name, tracks)
    content += labels_section(genre_name, tracks)
    content += years_section(genre_name, tracks)

    tracks_content = tracks_section(genre_name, tracks)

    with open(genre_overview_path(genre_name), "w") as f:
        f.write("\n".join(content))

    with open(genre_tracks_path(genre_name), "w") as f:
        f.write("\n".join(tracks_content))

    make_audio_features_page(tracks, genre_name, genre_audio_features_path(genre_name), genre_audio_features_chart_path(genre_name))


def title(genre_name):
    return [f"# {genre_name}", ""]


def artists_section(genre_name, tracks: pd.DataFrame):
    img = artists_bar_chart(tracks, genre_artist_graph_path(genre_name), genre_artist_graph_path(genre_name, genre_path(genre_name)))
    table_data = artists_table(tracks, genre_path(genre_name))

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    dp = DataProvider()
    scatterplot = comparison_scatter_plot(
        tracks, 
        tracks["track_uri"].apply(lambda uri: dp.primary_artist(uri)['artist_name']), 
        "Artist", 
        genre_artist_comparison_scatterplot_path(genre_name), 
        genre_artist_comparison_scatterplot_path(genre_name, genre_path(genre_name))
    )

    return ["## Top Artists", "", full_list, "", img, "", scatterplot]


def albums_section(genre_name, tracks: pd.DataFrame):
    img = albums_bar_chart(tracks, genre_album_graph_path(genre_name), genre_album_graph_path(genre_name, genre_path(genre_name)))
    table_data = albums_table(tracks)

    summary = f"See all {len(table_data)} albums"
    if len(table_data) > 100:
        summary = "See top 100 albums"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Albums", "", full_list, "", img, ""]


def labels_section(genre_name, tracks: pd.DataFrame):
    img = labels_bar_chart(tracks, genre_label_graph_path(genre_name), genre_label_graph_path(genre_name, genre_path(genre_name)))
    table_data = labels_table(tracks, genre_path(genre_name))

    summary = f"See all {len(table_data)} labels"
    if len(table_data) > 100:
        summary = "See top 100 labels"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Record Labels", "", full_list, "", img, ""]


def years_section(genre_name: str, tracks: pd.DataFrame):
    all_years = tracks.groupby('album_release_year').agg({'track_uri': 'count'}).reset_index()
    all_years = all_years.rename(columns={'album_release_year': 'Year', 'track_uri': 'Number of Tracks'})

    all_years = all_years.sort_values(by="Year", ascending=False)
    
    if len(all_years) >= 4:
        bar_chart = years_bar_chart(tracks, genre_years_graph_path(genre_name), genre_years_graph_path(genre_name, genre_path(genre_name)))
    else:
        bar_chart = ""

    return [
        '## Years', 
        "",
        bar_chart,
        "",
        newest_and_oldest_albums(tracks)
    ]


def tracks_section(genre_name: str, tracks: pd.DataFrame):
    display_tracks = tracks_table(tracks, genre_path(genre_name))
    table = md_table(display_tracks)
    return [f"# Tracks in {genre_name}", "", table, ""]
