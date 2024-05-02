import pandas as pd
from data.provider import DataProvider

from summarize.figures.albums_bar_chart import albums_bar_chart
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.genres_bar_chart import genres_bar_chart
from summarize.figures.labels_bar_chart import labels_bar_chart
from summarize.figures.producers_bar_chart import producers_bar_chart
from summarize.figures.top_tracks_score_time_series import top_tracks_score_time_series
from summarize.figures.years_bar_chart import years_bar_chart
from summarize.pages.track_features import make_track_features_page
from summarize.pages.clusters import make_clusters_page
from summarize.tables.albums_table import albums_table
from summarize.tables.artists_table import artists_table
from summarize.tables.genres_table import genres_table
from summarize.tables.labels_table import labels_table
from summarize.tables.producers_table import producers_table
from summarize.tables.top_tracks_table import most_and_least_listened_tracks_table
from summarize.tables.tracks_table import tracks_table
from utils.track_features import comparison_scatter_plot
from utils.date import newest_and_oldest_albums
from utils.markdown import md_link, md_table, md_image, md_summary_details, md_truncated_table
import utils.path as p
from utils.util import spotify_url


def make_playlist_summary(playlist_uri: str, tracks: pd.DataFrame):
    playlist = None if playlist_uri is None else DataProvider().playlist(playlist_uri)
    playlist_name = 'Liked Tracks' if playlist is None else playlist["playlist_name"]
    playlist_image_url = None if playlist is None else playlist["playlist_image_url"]

    print(f"Generating summary for playlist {playlist_name}")
    
    content = []
    content += title(playlist_name)
    content += image(playlist_name, playlist_image_url)
    content += tracks_link(playlist_uri, tracks)
    if len(tracks) > 10:
        content += [md_link(f"See Track Features", p.playlist_audio_features_path(playlist_name, p.playlist_path(playlist_name))), ""]
        content += [md_link(f"See Clusters", p.playlist_clusters_path(playlist_name, p.playlist_path(playlist_name))), ""]
    content += artists_section(playlist_name, tracks)
    content += tracks_section(playlist_name, tracks)
    content += albums_section(playlist_name, tracks)
    content += labels_section(playlist_name, tracks)
    content += genres_section(playlist_name, tracks)
    content += producers_section(playlist_name, tracks)
    content += years_section(playlist_name, tracks)

    with open(p.playlist_overview_path(playlist_name), "w") as f:
        f.write("\n".join(content))

    if len(tracks) > 10:
        make_track_features_page(tracks, playlist_name, p.playlist_audio_features_path(playlist_name), p.playlist_audio_features_figure_path(playlist_name))

    if len(tracks) > 50:
        make_clusters_page(tracks, playlist_name, p.playlist_clusters_path(playlist_name), p.playlist_clusters_figure_path(playlist_name))


def title(playlist_name):
    return [f"# {playlist_name}", ""]


def image(playlist_name, playlist_image_url):
    if playlist_image_url is None:
        return []
        
    return ["", md_image(playlist_name, playlist_image_url, 100), ""]


def tracks_link(playlist_uri: str, tracks: pd.DataFrame):
    track_count = len(tracks)
    liked_track_count = tracks["track_liked"].sum()
    text = f"{track_count} tracks" if track_count == liked_track_count else f"{track_count} tracks ({liked_track_count} liked)"

    # The Liked Songs playlist has no URI
    if playlist_uri is None:
        return [text, ""]

    return [md_link(text + " 🔗", spotify_url(playlist_uri)), ""]


def artists_section(playlist_name, playlist_full: pd.DataFrame):
    img = artists_bar_chart(playlist_full, p.playlist_artist_graph_path(playlist_name), p.playlist_artist_graph_path(playlist_name, p.playlist_path(playlist_name)))
    table_data = artists_table(playlist_full, p.playlist_path(playlist_name))

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    if len(table_data) >= 10:
        scatterplot = comparison_scatter_plot(
            playlist_full, 
            playlist_full["primary_artist_name"], 
            "Artist", 
            p.playlist_artist_comparison_scatterplot_path(playlist_name), 
            p.playlist_artist_comparison_scatterplot_path(playlist_name, p.playlist_path(playlist_name))
        )
    else:
        scatterplot = ""

    return ["## Top Artists", "", full_list, "", img, "", scatterplot , ""]


def albums_section(playlist_name, playlist_full: pd.DataFrame):
    img = albums_bar_chart(playlist_full, p.playlist_album_graph_path(playlist_name), p.playlist_album_graph_path(playlist_name, p.playlist_path(playlist_name)))
    table_data = albums_table(playlist_full)

    summary = f"See all {len(table_data)} albums"
    if len(table_data) > 100:
        summary = "See top 100 albums"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Albums", "", full_list, "", img, ""]


def labels_section(playlist_name, playlist_full: pd.DataFrame):
    img = labels_bar_chart(playlist_full, p.playlist_label_graph_path(playlist_name), p.playlist_label_graph_path(playlist_name, p.playlist_path(playlist_name)))
    table_data = labels_table(playlist_full, p.playlist_path(playlist_name))

    summary = f"See all {len(table_data)} labels"
    if len(table_data) > 100:
        summary = "See top 100 labels"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Record Labels", "", full_list, "", img, ""]


def genres_section(playlist_name: str, tracks: pd.DataFrame):
    img = genres_bar_chart(tracks, p.playlist_genre_graph_path(playlist_name), p.playlist_genre_graph_path(playlist_name, p.playlist_path(playlist_name)))
    table_data = genres_table(tracks, p.playlist_path(playlist_name))
    
    summary = f"See all {len(table_data)} genres"
    if len(table_data) > 100:
        summary = "See top 100 genres"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Genres", "", full_list, "", img, ""]


def producers_section(playlist_name, tracks: pd.DataFrame):
    producers = producers_table(tracks, p.playlist_path(playlist_name))

    if len(producers) == 0:
        return []
    
    bar_chart = producers_bar_chart(
        tracks, 
        p.playlist_producers_graph_path(playlist_name),
        p.playlist_producers_graph_path(playlist_name, p.playlist_path(playlist_name)))
    
    return [
        '## Top Producers',
        '',
        md_truncated_table(producers),
        '',
        bar_chart,
        ''
    ]


def tracks_section(playlist_name: str, tracks: pd.DataFrame):
    return [
        '## Top Tracks',
        '',
        top_tracks_score_time_series(tracks, p.playlist_top_tracks_time_series_path(playlist_name), p.playlist_top_tracks_time_series_path(playlist_name, p.playlist_path(playlist_name))),
        '',
        md_summary_details('Most and least listened tracks', most_and_least_listened_tracks_table(tracks, p.playlist_path(playlist_name)))
    ]


def years_section(playlist_name: str, tracks: pd.DataFrame):
    all_years = tracks.groupby('album_release_year').agg({'track_uri': 'count'}).reset_index()
    all_years = all_years.rename(columns={'album_release_year': 'Year', 'track_uri': 'Number of Tracks'})

    years_with_page = set(all_years[all_years['Number of Tracks'] >= 20]["Year"])

    all_years = all_years.sort_values(by="Year", ascending=False)
    all_years["Year"] = all_years["Year"].apply(lambda y: y if y not in years_with_page else md_link(y, p.playlist_year_overview_path(playlist_name, y, p.playlist_path(playlist_name))))
    
    if len(all_years) >= 4:
        bar_chart = years_bar_chart(tracks, p.playlist_years_graph_path(playlist_name), p.playlist_years_graph_path(playlist_name, p.playlist_path(playlist_name)))
    else:
        bar_chart = ""

    if len(years_with_page) > 0:
        table_section = md_summary_details('View all years', md_table(all_years))
    else:
        table_section = ""

    for year in years_with_page:
        page_content = year_page(playlist_name, year, tracks)
        with open(p.playlist_year_overview_path(playlist_name, year), "w") as f:
            f.write("\n".join(page_content))

    return [
        '## Years', 
        "",
        table_section,
        "",
        bar_chart,
        "",
        newest_and_oldest_albums(tracks)
    ]


def year_page(playlist_name: str, year: str, tracks: pd.DataFrame):
    tracks_for_year = tracks[tracks["album_release_year"] == year]
    return [
        f"# Tracks in {playlist_name} from {year}",
        "",
        "## Artists",
        "",
        md_truncated_table(artists_table(tracks_for_year, p.playlist_year_path(playlist_name, year)), 10),
        "",
        "## Albums",
        "",
        md_truncated_table(albums_table(tracks_for_year), 10),
        "",
        "## Tracks",
        "",
        top_tracks_score_time_series(
            tracks_for_year, 
            p.playlist_year_tracks_time_series_path(playlist_name, year), 
            p.playlist_year_tracks_time_series_path(playlist_name, year, p.playlist_year_path(playlist_name, year))
        ),
        "",
        md_truncated_table(tracks_table(tracks_for_year, p.playlist_year_path(playlist_name, year), sorting="default"), 10),
        ""
    ]
