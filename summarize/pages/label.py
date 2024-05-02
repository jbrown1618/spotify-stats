import pandas as pd
from summarize.figures.albums_bar_chart import albums_bar_chart
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.genres_bar_chart import genres_bar_chart
from summarize.figures.producers_bar_chart import producers_bar_chart
from summarize.pages.track_features import make_track_features_page
from summarize.pages.clusters import make_clusters_page
from summarize.tables.albums_table import albums_table
from summarize.tables.artists_table import artists_table
from summarize.tables.genres_table import genres_table
from summarize.tables.producers_table import producers_table
from summarize.tables.tracks_table import tracks_table
from utils.markdown import md_link, md_truncated_table
import utils.path as p

def make_label_summary(label_name: str, tracks: pd.DataFrame):
    print(f"Generating summary for label {label_name}")
    
    content = []
    content += title(label_name)
    content += [f"{len(tracks)} songs", ""]
    if len(tracks) > 10:
        content += [md_link(f"See Track Features", p.label_audio_features_path(label_name, p.label_path(label_name))), ""]
        content += [md_link(f"See Clusters", p.label_clusters_path(label_name, p.label_path(label_name))), ""]
    content += aliases(tracks)
    content += artists_section(label_name, tracks)
    content += albums_section(label_name, tracks)
    content += genres_section(label_name, tracks)
    content += producers_section(label_name, tracks)
    content += tracks_section(label_name, tracks)

    with open(p.label_overview_path(label_name), "w") as f:
        f.write("\n".join(content))

    if len(tracks) > 10:
        make_track_features_page(tracks, label_name, p.label_audio_features_path(label_name), p.label_audio_features_chart_path(label_name))



def title(label_name):
    return [f"# {label_name}", ""]


def aliases(label_full: pd.DataFrame):
    label_aliases = label_full.groupby("album_label").agg({"track_uri": "count"}).reset_index()
    label_aliases = label_aliases.sort_values(by="track_uri", ascending=False)

    if label_aliases.size < 2: return []

    return ["Appears as:"] + [
        f"- {alias['album_label']} ({alias['track_uri']} tracks)"
        for i, alias in label_aliases.iterrows()
    ] + [""]


def artists_section(label_name, label_full: pd.DataFrame):
    img = artists_bar_chart(label_full, p.label_artist_graph_path(label_name), p.label_artist_graph_path(label_name, p.label_path(label_name)))
    table_data = artists_table(label_full, p.label_path(label_name))

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Artists", "", full_list, "", img, ""]


def albums_section(label_name, label_full: pd.DataFrame):
    img = albums_bar_chart(label_full, p.label_album_graph_path(label_name), p.label_album_graph_path(label_name, p.label_path(label_name)))
    table_data = albums_table(label_full)

    summary = f"See all {len(table_data)} albums"
    if len(table_data) > 100:
        summary = "See top 100 albums"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Top Albums", "", full_list, "", img, ""]


def genres_section(label_name: str, tracks: pd.DataFrame):
    img = genres_bar_chart(tracks, p.label_genre_graph_path(label_name), p.label_genre_graph_path(label_name, p.label_path(label_name)))
    table_data = genres_table(tracks, p.label_path(label_name))
    
    summary = f"See all {len(table_data)} genres"
    if len(table_data) > 100:
        summary = "See top 100 genres"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Genres", "", full_list, "", img, ""]


def producers_section(label_name, tracks: pd.DataFrame):
    producers = producers_table(tracks, p.label_path(label_name))

    if len(producers) == 0:
        return []
    
    bar_chart = producers_bar_chart(
        tracks, 
        p.label_producers_graph_path(label_name),
        p.label_producers_graph_path(label_name, p.label_path(label_name)))
    
    return [
        '## Top Producers',
        '',
        md_truncated_table(producers),
        '',
        bar_chart
    ]


def tracks_section(label_name: str, label_full: pd.DataFrame):
    display_tracks = tracks_table(label_full, p.label_path(label_name), sorting='default')
    table = md_truncated_table(display_tracks, 10, "See all tracks")
    return [f"## Tracks released under {label_name}", "", table, ""]
