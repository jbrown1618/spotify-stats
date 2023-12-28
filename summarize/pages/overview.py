import typing
import pandas as pd
from data.provider import DataProvider
from data.raw import RawData
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.genres_bar_chart import genres_bar_chart
from summarize.figures.labels_bar_chart import labels_bar_chart
from summarize.figures.producers_bar_chart import producers_bar_chart
from summarize.figures.top_artists_time_series import top_artists_time_series
from summarize.figures.top_tracks_time_series import top_tracks_time_series
from summarize.pages.track_features import make_track_features_page
from summarize.pages.clusters import make_clusters_page
from summarize.tables.artists_table import artists_table
from summarize.tables.genres_table import genres_table
from summarize.tables.labels_table import labels_table
from summarize.tables.playlists_table import playlists_table
from summarize.tables.producers_table import producers_table
from summarize.tables.top_artists_table import top_artists_table
from summarize.tables.top_tracks_table import top_tracks_table
from utils.top_lists import get_term_length_phrase, graphable_top_list_terms
from utils.track_features import comparison_scatter_plot
from utils.markdown import md_link, md_summary_details, md_truncated_table
from utils.path import errors_path, overview_artist_graph_path, overview_artists_scatterplot_path, overview_audio_features_figure_path, overview_audio_features_path, overview_clusters_figure_path, overview_clusters_path, overview_genre_graph_path, overview_genres_scatterplot_path, overview_label_graph_path, overview_playlists_scatterplot_path, overview_path, overview_producers_graph_path, overview_top_artists_time_series_path, overview_top_tracks_time_series_path
from utils.settings import output_dir


def make_overview(tracks_full: pd.DataFrame):
    print("Generating Overview")

    content = []

    content += title("jbrown1618")
    content += byline()
    content += [md_link(f"See Track Features", overview_audio_features_path(output_dir())), ""]
    content += [md_link(f"See Clusters", overview_clusters_path(output_dir())), ""]
    content += playlists_section()
    content += artists_section(tracks_full)
    content += tracks_section(tracks_full)
    content += genres_section(tracks_full)
    content += labels_section(tracks_full)
    content += producers_section(tracks_full)
    content += errors()

    with open(overview_path(), "w") as f:
        f.write("\n".join(content))

    make_track_features_page(tracks_full, "All Tracks", overview_audio_features_path(), overview_audio_features_figure_path())
    make_clusters_page(tracks_full, "All tracks", overview_clusters_path(), overview_clusters_figure_path())


def title(user: str):
    return [f"# Spotify Summary for {user}", ""]


def byline():
    return [f"Generated by {md_link('jbrown1618/spotify-stats', 'https://github.com/jbrown1618/spotify-stats')}", ""]


def errors():
    return ['## Possible organizational errors', md_link("Possible organizational errors", errors_path(output_dir()))]


def tracks_section(tracks: pd.DataFrame):
    images = [
        md_summary_details(
            f'Top tracks of {get_term_length_phrase(term)} over time', 
            top_tracks_time_series(
                term, 
                10, 
                overview_top_tracks_time_series_path(term), 
                overview_top_tracks_time_series_path(term, output_dir())
            )
        )
        for term in graphable_top_list_terms
    ]

    contents = [
        "## Tracks", 
        "", 
        "Top tracks of the last month, six months, and all time",
        "",
        md_truncated_table(top_tracks_table(tracks), 10, "See top 50 tracks"), 
        ""
    ]

    return contents + images


def playlists_section():
    dp = DataProvider()
    table = md_truncated_table(playlists_table(output_dir()), 10)

    playlists_sorted_by_track_count = dp.playlists().sort_values(by="playlist_track_count", ascending=False)["playlist_uri"]

    main_playlist_col = dp.tracks()["track_uri"]\
        .apply(lambda track_uri: get_main_playlist(track_uri, playlists_sorted_by_track_count))
    
    scatter = comparison_scatter_plot(dp.tracks(), main_playlist_col, "Playlist", overview_playlists_scatterplot_path(), overview_playlists_scatterplot_path(output_dir()))
    
    return [
        "## Playlists", 
        "", 
        table, 
        "", 
        scatter, 
        ""
    ]


def artists_section(tracks: pd.DataFrame):
    time_series_images = [
        md_summary_details(
            f'Top artists of {get_term_length_phrase(term)} over time', 
            top_artists_time_series(
                term, 
                10, 
                overview_top_artists_time_series_path(term), 
                overview_top_artists_time_series_path(term, output_dir())
            )
        )
        for term in graphable_top_list_terms
    ]

    top_artists = md_truncated_table(top_artists_table(), 10, "See top 50 artists")
    
    bar_chart = artists_bar_chart(tracks, overview_artist_graph_path(), overview_artist_graph_path(output_dir()))
    table_data = artists_table(tracks, output_dir())

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    if len(table_data) >= 10:
        scatterplot = comparison_scatter_plot(
            tracks, 
            tracks["primary_artist_name"], 
            "Artist", 
            overview_artists_scatterplot_path(), 
            overview_artists_scatterplot_path(output_dir())
        )
    else:
        scatterplot = ""

    return [
        "## Artists", 
        "", 
        "Top artists of the last month, six months, and all time",
        "",
        top_artists,
        ""
    ] + time_series_images + [
        "",
        "Artists by number of liked tracks",
        full_list, 
        "", 
        bar_chart, 
        "", 
        scatterplot, 
        ""
    ]


def genres_section(tracks: pd.DataFrame):
    img = genres_bar_chart(tracks, overview_genre_graph_path(), overview_genre_graph_path(output_dir()))
    main_genre_col = tracks["track_uri"].apply(get_main_genre)
    scatter = comparison_scatter_plot(tracks, main_genre_col, "Genre", overview_genres_scatterplot_path(), overview_genres_scatterplot_path(output_dir()))

    table_data = genres_table(tracks, output_dir())
    
    summary = f"See all {len(table_data)} genres"
    if len(table_data) > 100:
        summary = "See top 100 genres"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Genres", "", full_list, "", img, "", scatter, ""]


def get_main_genre(track_uri: str):
    track_genre = DataProvider().track_genre()
    subset = track_genre[track_genre["track_uri"] == track_uri]
    if len(subset) == 0:
        return "None"

    return subset.iloc[0]["genre"]


def get_main_playlist(track_uri: str, playlists_sorted_by_track_count: typing.Iterable[str]):
    playlists = DataProvider().playlists()
    playlist_track = RawData()['playlist_track']

    playlist_uris = set(playlist_track[playlist_track["track_uri"] == track_uri]["playlist_uri"])
    for playlist_uri in playlists_sorted_by_track_count:
        if playlist_uri in playlist_uris:
            return playlists[playlists["playlist_uri"] == playlist_uri].iloc[0]["playlist_name"]
    return "None"


def labels_section(tracks: pd.DataFrame):
    img = labels_bar_chart(tracks, overview_label_graph_path(), overview_label_graph_path(output_dir()))
    table_data = labels_table(tracks, output_dir())

    summary = f"See all {len(table_data)} labels"
    if len(table_data) > 100:
        summary = "See top 100 labels"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Record Labels", "", full_list, "", img, ""]



def producers_section(tracks: pd.DataFrame):
    producers = producers_table(tracks, output_dir())

    if len(producers) == 0:
        return []
    
    bar_chart = producers_bar_chart(
        tracks, 
        overview_producers_graph_path(),
        overview_producers_graph_path(output_dir()))
    
    return [
        '## Top Producers',
        '',
        md_truncated_table(producers),
        '',
        bar_chart
    ]
