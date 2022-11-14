import pandas as pd
from summarize.figures.albums_bar_chart import albums_bar_chart
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.tables.albums_table import albums_table
from summarize.tables.artists_table import artists_table
from summarize.tables.tracks_table import tracks_table

from utils.path import label_album_graph_path, label_artist_graph_path, label_path, labels_path
from utils.util import md_summary_details


def make_label_summary(label_name: str, label_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    print(f"Generating summary for label {label_name}")
    
    content = []
    content += title(label_name)
    content += [f"{len(label_full)} songs", ""]
    content += aliases(label_full)
    content += artists_section(label_name, label_full, track_artist_full)
    content += albums_section(label_name, label_full)
    content += tracks_section(label_name, label_full, track_artist_full)

    with open(label_path(label_name), "w") as f:
        f.write("\n".join(content))


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


def artists_section(label_name, label_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    img = artists_bar_chart(label_full, track_artist_full, label_artist_graph_path(label_name), label_artist_graph_path(label_name, labels_path()))
    table_data = artists_table(label_full, track_artist_full, labels_path())

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Top Artists", "", img, "", full_list, ""]


def albums_section(label_name, label_full: pd.DataFrame):
    img = albums_bar_chart(label_full, label_album_graph_path(label_name), label_album_graph_path(label_name, labels_path()))
    table_data = albums_table(label_full)

    summary = f"See all {len(table_data)} albums"
    if len(table_data) > 100:
        summary = "See top 100 albums"
        table_data = table_data.head(100)

    full_list = md_summary_details(summary, table_data.to_markdown(index=False))

    return ["## Top Albums", "", img, "", full_list, ""]


def tracks_section(label_name: str, label_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = tracks_table(label_full, track_artist_full, labels_path())
    table = display_tracks.to_markdown(index=False)
    return [f"## Tracks released under {label_name}", "", table, ""]
