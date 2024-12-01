import pandas as pd

from summarize.figures.albums_bar_chart import albums_bar_chart
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.labels_bar_chart import labels_bar_chart
from summarize.figures.producers_bar_chart import producers_bar_chart
from summarize.figures.years_bar_chart import years_bar_chart
from summarize.tables.albums_table import albums_table
from summarize.tables.artists_table import artists_table
from summarize.tables.labels_table import labels_table
from summarize.tables.producers_table import producers_table
from summarize.tables.top_tracks_table import most_and_least_listened_tracks_table
from utils.date import newest_and_oldest_albums
from utils.markdown import md_truncated_table
import utils.path as p

def make_genre_summary(genre_name: str, tracks: pd.DataFrame):
    print(f"Generating summary for genre {genre_name}")
    
    content = []
    content += title(genre_name)
    content += [f"{len(tracks)} songs", ""]
    content += artists_section(genre_name, tracks)
    content += most_and_least_listened_tracks_section(genre_name, tracks)
    content += albums_section(genre_name, tracks)
    content += labels_section(genre_name, tracks)
    content += producers_section(genre_name, tracks)
    content += years_section(genre_name, tracks)

    with open(p.genre_overview_path(genre_name), "w") as f:
        f.write("\n".join(content))


def title(genre_name):
    return [f"# {genre_name}", ""]


def artists_section(genre_name, tracks: pd.DataFrame):
    img = artists_bar_chart(tracks, p.genre_artist_graph_path(genre_name), p.genre_artist_graph_path(genre_name, p.genre_path(genre_name)))
    table_data = artists_table(tracks, p.genre_path(genre_name))

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Artists", "", full_list, "", img]


def most_and_least_listened_tracks_section(genre_name: str, tracks: pd.DataFrame):
    return [
        '## Most and least listened tracks',
        most_and_least_listened_tracks_table(tracks, p.genre_path(genre_name)),
        ''
    ]


def albums_section(genre_name, tracks: pd.DataFrame):
    img = albums_bar_chart(tracks, p.genre_album_graph_path(genre_name), p.genre_album_graph_path(genre_name, p.genre_path(genre_name)))
    table_data = albums_table(tracks)

    summary = f"See all {len(table_data)} albums"
    if len(table_data) > 100:
        summary = "See top 100 albums"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Albums", "", full_list, "", img, ""]


def labels_section(genre_name, tracks: pd.DataFrame):
    img = labels_bar_chart(tracks, p.genre_label_graph_path(genre_name), p.genre_label_graph_path(genre_name, p.genre_path(genre_name)))
    table_data = labels_table(tracks, p.genre_path(genre_name))

    summary = f"See all {len(table_data)} labels"
    if len(table_data) > 100:
        summary = "See top 100 labels"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Record Labels", "", full_list, "", img, ""]


def producers_section(genre_name, tracks: pd.DataFrame):
    producers = producers_table(tracks, p.genre_path(genre_name))

    if len(producers) == 0:
        return []
    
    bar_chart = producers_bar_chart(
        tracks, 
        p.genre_producers_graph_path(genre_name),
        p.genre_producers_graph_path(genre_name, p.genre_path(genre_name)))
    
    return [
        '## Top Producers',
        '',
        bar_chart,
        '',
        md_truncated_table(producers)
    ]


def years_section(genre_name: str, tracks: pd.DataFrame):
    all_years = tracks.groupby('album_release_year').agg({'track_uri': 'count'}).reset_index()
    all_years = all_years.rename(columns={'album_release_year': 'Year', 'track_uri': 'Number of Tracks'})

    all_years = all_years.sort_values(by="Year", ascending=False)
    
    if len(all_years) >= 4:
        bar_chart = years_bar_chart(tracks, p.genre_years_graph_path(genre_name), p.genre_years_graph_path(genre_name, p.genre_path(genre_name)))
    else:
        bar_chart = ""

    return [
        '## Years', 
        "",
        newest_and_oldest_albums(tracks),
        "",
        bar_chart
    ]
