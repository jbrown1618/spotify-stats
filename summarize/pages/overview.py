import typing
import pandas as pd
from data.provider import DataProvider
from data.raw import RawData
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.genres_bar_chart import genres_bar_chart
from summarize.figures.labels_bar_chart import labels_bar_chart
from summarize.figures.producers_bar_chart import producers_bar_chart
from summarize.figures.top_albums_score_time_series import top_albums_score_time_series
from summarize.figures.top_artists_score_time_series import top_artists_score_time_series
from summarize.figures.top_artists_time_series import top_artists_time_series
from summarize.figures.top_tracks_score_time_series import top_tracks_score_time_series
from summarize.figures.top_tracks_time_series import top_tracks_time_series
from summarize.pages.track_features import make_track_features_page
from summarize.pages.clusters import make_clusters_page
from summarize.tables.artists_table import artists_table
from summarize.tables.genres_table import genres_table
from summarize.tables.labels_table import labels_table
from summarize.tables.playlists_table import playlists_table
from summarize.tables.producers_table import producers_table
from summarize.tables.top_artists_table import top_artists_table
from summarize.tables.top_tracks_table import most_and_least_listened_tracks_table, top_tracks_table
from summarize.tables.tracks_table import tracks_table
from utils.top_lists import get_term_length_phrase, graphable_top_list_terms_for_tracks, graphable_top_list_terms_for_artists
from utils.track_features import comparison_scatter_plot
from utils.markdown import md_link, md_summary_details, md_table, md_truncated_table
import utils.path as p
from utils.settings import output_dir


def make_overview(tracks_full: pd.DataFrame):
    print("Generating Overview")

    content = []

    content += title("jbrown1618")
    content += byline()
    content += [md_link(f"See Track Features", p.overview_audio_features_path(output_dir())), ""]
    content += [md_link(f"See Clusters", p.overview_clusters_path(output_dir())), ""]
    content += playlists_section()
    content += artists_section(tracks_full)
    content += tracks_section(tracks_full)
    content += albums_section(tracks_full)
    content += genres_section(tracks_full)
    content += labels_section(tracks_full)
    content += producers_section(tracks_full)
    content += errors()

    with open(p.overview_path(), "w") as f:
        f.write("\n".join(content))

    make_track_features_page(tracks_full, "All Tracks", p.overview_audio_features_path(), p.overview_audio_features_figure_path())
    make_clusters_page(tracks_full, "All tracks", p.overview_clusters_path(), p.overview_clusters_figure_path())


def title(user: str):
    return [f"# Spotify Summary for {user}", ""]


def byline():
    return [f"Generated by {md_link('jbrown1618/spotify-stats', 'https://github.com/jbrown1618/spotify-stats')}", ""]


def errors():
    return ['## Possible organizational errors', md_link("Possible organizational errors", p.errors_path(output_dir()))]


def tracks_section(tracks: pd.DataFrame):
    return [
        "## Tracks", 
        "",
        "### Top Tracks of All Time",
        "",
        md_truncated_table(tracks_table(tracks.sort_values("track_rank", ascending=True).head(100), output_dir()), 10, "View top 100 tracks"),
        "",
        top_tracks_score_time_series(
            tracks,
            p.overview_top_tracks_time_series_path('score'),
            p.overview_top_tracks_time_series_path('score', output_dir())
        ),
        "", 
        md_summary_details(
            "Top tracks of the last month, six months, and year", 
            md_table(top_tracks_table(tracks, output_dir()))
        ),
        "",
    ] + [
        md_summary_details(
            f'Top tracks of {get_term_length_phrase(term)} over time', 
            top_tracks_time_series(
                term, 
                10, 
                p.overview_top_tracks_time_series_path(term), 
                p.overview_top_tracks_time_series_path(term, output_dir())
            )
        )
        for term in graphable_top_list_terms_for_tracks
    ]


def playlists_section():
    dp = DataProvider()
    table = md_truncated_table(playlists_table(output_dir()), 10)

    playlists_sorted_by_track_count = dp.playlists().sort_values(by="playlist_track_count", ascending=False)["playlist_uri"]

    main_playlist_col = dp.tracks()["track_uri"]\
        .apply(lambda track_uri: get_main_playlist(track_uri, playlists_sorted_by_track_count))
    
    scatter = comparison_scatter_plot(dp.tracks(), main_playlist_col, "Playlist", p.overview_playlists_scatterplot_path(), p.overview_playlists_scatterplot_path(output_dir()))
    
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
                p.overview_top_artists_time_series_path(term), 
                p.overview_top_artists_time_series_path(term, output_dir())
            )
        )
        for term in graphable_top_list_terms_for_artists
    ]

    rank_time_series = top_artists_score_time_series(
        tracks['primary_artist_uri'], 
        p.overview_top_artists_time_series_path("score"), 
        p.overview_top_artists_time_series_path("score", output_dir())
    )

    top_artists = md_table(top_artists_table())
    
    bar_chart = artists_bar_chart(tracks, p.overview_artist_graph_path(), p.overview_artist_graph_path(output_dir()))
    table_data = artists_table(tracks, output_dir(), "rank")

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return [
        "## Artists", 
        "", 
        "### Top artists of all time",
        "",
        rank_time_series,
        "",
        full_list,
        "",
        md_summary_details("Top artists of the last month, last 6 months, and last year", top_artists),
        "",
        ""
    ] + time_series_images + [
        "",
        "### Artists by number of liked tracks",
        "", 
        bar_chart,
        ""
    ]


def albums_section(tracks: pd.DataFrame):
    return [
        "## Albums",
        "",
        "Top albums over time",
        "",
        top_albums_score_time_series(
            tracks, 
            p.overview_top_albums_time_series_path("score"), 
            p.overview_top_albums_time_series_path("score", output_dir())
        ),
        ""
    ]


def genres_section(tracks: pd.DataFrame):
    img = genres_bar_chart(tracks, p.overview_genre_graph_path(), p.overview_genre_graph_path(output_dir()))
    main_genre_col = tracks["track_uri"].apply(get_main_genre)
    scatter = comparison_scatter_plot(tracks, main_genre_col, "Genre", p.overview_genres_scatterplot_path(), p.overview_genres_scatterplot_path(output_dir()))

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
    img = labels_bar_chart(tracks, p.overview_label_graph_path(), p.overview_label_graph_path(output_dir()))
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
        p.overview_producers_graph_path(),
        p.overview_producers_graph_path(output_dir()))
    
    return [
        '## Top Producers',
        '',
        md_truncated_table(producers),
        '',
        bar_chart
    ]
