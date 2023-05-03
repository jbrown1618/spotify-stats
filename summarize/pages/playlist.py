import pandas as pd

from summarize.figures.albums_bar_chart import albums_bar_chart
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.genres_bar_chart import genres_bar_chart
from summarize.figures.labels_bar_chart import labels_bar_chart
from summarize.figures.years_bar_chart import years_bar_chart
from summarize.pages.audio_features import make_audio_features_page
from summarize.tables.albums_table import albums_table
from summarize.tables.artists_table import artists_table
from summarize.tables.genres_table import genres_table
from summarize.tables.labels_table import labels_table
from summarize.tables.tracks_table import tracks_table
from utils.artist import get_primary_artist_name
from utils.audio_features import comparison_scatter_plot
from utils.date import newest_and_oldest_albums
from utils.markdown import md_link, md_table, md_image, md_summary_details, md_truncated_table
from utils.path import playlist_album_graph_path, playlist_audio_features_chart_path, playlist_audio_features_path, playlist_genre_graph_path, playlist_label_graph_path, playlist_overview_path, playlist_path, playlist_tracks_path, playlist_artist_comparison_scatterplot_path, playlist_artist_graph_path, playlist_year_path, playlist_years_graph_path


def make_playlist_summary(tracks: pd.DataFrame, track_artist_full: pd.DataFrame, is_liked_songs=False):
    playlist_name = "Liked Tracks" if is_liked_songs else tracks["playlist_name"].iloc[0]
    playlist_image_url = None if is_liked_songs else tracks["playlist_image_url"].iloc[0]
    print(f"Generating summary for playlist {playlist_name}")
    
    content = []
    content += title(playlist_name)
    content += image(playlist_name, playlist_image_url)
    content += tracks_link(playlist_name, tracks)
    content += [md_link(f"See Audio Features", playlist_audio_features_path(playlist_name, playlist_path(playlist_name))), ""]
    content += artists_section(playlist_name, tracks, track_artist_full)
    content += albums_section(playlist_name, tracks)
    content += labels_section(playlist_name, tracks)
    content += genres_section(playlist_name, tracks)
    content += years_section(playlist_name, tracks, track_artist_full)

    tracks_content = tracks_section(playlist_name, tracks, track_artist_full)

    with open(playlist_overview_path(playlist_name), "w") as f:
        f.write("\n".join(content))

    with open(playlist_tracks_path(playlist_name), "w") as f:
        f.write("\n".join(tracks_content))

    make_audio_features_page(tracks, playlist_name, playlist_audio_features_path(playlist_name), playlist_audio_features_chart_path(playlist_name))


def title(playlist_name):
    return [f"# {playlist_name}", ""]


def image(playlist_name, playlist_image_url):
    if playlist_image_url is None:
        return []
        
    return ["", md_image(playlist_name, playlist_image_url, 100), ""]


def tracks_link(playlist_name: str, tracks: pd.DataFrame):
    track_count = len(tracks)
    liked_track_count = tracks["track_liked"].sum()
    text = f"{track_count} songs" if track_count == liked_track_count else f"{track_count} songs ({liked_track_count} liked)"
    return [md_link(text, playlist_tracks_path(playlist_name, playlist_path(playlist_name))), ""]


def artists_section(playlist_name, playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    img = artists_bar_chart(playlist_full, track_artist_full, playlist_artist_graph_path(playlist_name), playlist_artist_graph_path(playlist_name, playlist_path(playlist_name)))
    table_data = artists_table(playlist_full, track_artist_full, playlist_path(playlist_name))

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    if len(table_data) >= 10:
        scatterplot = comparison_scatter_plot(
            playlist_full, 
            playlist_full["track_uri"].apply(lambda uri: get_primary_artist_name(uri, track_artist_full)), 
            "Artist", 
            playlist_artist_comparison_scatterplot_path(playlist_name), 
            playlist_artist_comparison_scatterplot_path(playlist_name, playlist_path(playlist_name))
        )
    else:
        scatterplot = ""

    return ["## Top Artists", "", full_list, "", img, "", scatterplot , ""]


def albums_section(playlist_name, playlist_full: pd.DataFrame):
    img = albums_bar_chart(playlist_full, playlist_album_graph_path(playlist_name), playlist_album_graph_path(playlist_name, playlist_path(playlist_name)))
    table_data = albums_table(playlist_full)

    summary = f"See all {len(table_data)} albums"
    if len(table_data) > 100:
        summary = "See top 100 albums"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Albums", "", full_list, "", img, ""]


def labels_section(playlist_name, playlist_full: pd.DataFrame):
    img = labels_bar_chart(playlist_full, playlist_label_graph_path(playlist_name), playlist_label_graph_path(playlist_name, playlist_path(playlist_name)))
    table_data = labels_table(playlist_full, playlist_path(playlist_name))

    summary = f"See all {len(table_data)} labels"
    if len(table_data) > 100:
        summary = "See top 100 labels"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Record Labels", "", full_list, "", img, ""]


def genres_section(playlist_name: str, tracks: pd.DataFrame):
    img = genres_bar_chart(tracks, playlist_genre_graph_path(playlist_name), playlist_genre_graph_path(playlist_name, playlist_path(playlist_name)))
    table_data = genres_table(tracks, playlist_path(playlist_name))
    
    summary = f"See all {len(table_data)} genres"
    if len(table_data) > 100:
        summary = "See top 100 genres"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Genres", "", full_list, "", img, ""]


def years_section(playlist_name: str, tracks: pd.DataFrame, track_artist_full: pd.DataFrame):
    all_years = tracks.groupby('album_release_year').agg({'track_uri': 'count'}).reset_index()
    all_years = all_years.rename(columns={'album_release_year': 'Year', 'track_uri': 'Number of Tracks'})

    years_with_page = set(all_years[all_years['Number of Tracks'] >= 20]["Year"])

    all_years = all_years.sort_values(by="Year", ascending=False)
    all_years["Year"] = all_years["Year"].apply(lambda y: y if y not in years_with_page else md_link(y, playlist_year_path(playlist_name, y, playlist_path(playlist_name))))
    
    if len(all_years) >= 4:
        bar_chart = years_bar_chart(tracks, playlist_years_graph_path(playlist_name), playlist_years_graph_path(playlist_name, playlist_path(playlist_name)))
    else:
        bar_chart = ""

    if len(years_with_page) > 0:
        table_section = md_summary_details('View all years', md_table(all_years))
    else:
        table_section = ""

    for year in years_with_page:
        page_content = year_page(playlist_name, year, tracks, track_artist_full)
        with open(playlist_year_path(playlist_name, year), "w") as f:
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


def year_page(playlist_name: str, year: str, tracks: pd.DataFrame, track_artist_full: pd.DataFrame):
    tracks_for_year = tracks[tracks["album_release_year"] == year]
    return [
        f"# Tracks in {playlist_name} from {year}",
        "",
        "## Artists",
        "",
        md_table(artists_table(tracks_for_year, track_artist_full, playlist_path(playlist_name))),
        "",
        "## Albums",
        "",
        md_table(albums_table(tracks_for_year)),
        "",
        "## Tracks",
        "",
        md_table(tracks_table(tracks_for_year, track_artist_full, playlist_path(playlist_name), chronological=True)),
        ""
    ]


def tracks_section(playlist_name: str, playlist_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = tracks_table(playlist_full, track_artist_full, playlist_path(playlist_name))
    table = md_table(display_tracks)
    return [f"# Tracks in {playlist_name}", "", table, ""]
