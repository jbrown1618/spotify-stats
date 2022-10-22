import pandas as pd

from utils.util import md_link
from utils.path import label_path

def labels_table(tracks: pd.DataFrame, album_record_label: pd.DataFrame, relative_to: str):
    grouped = pd.merge(tracks, album_record_label, on="album_uri").groupby("album_standardized_label").agg({"track_uri": "count"}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "album_standardized_label"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "album_standardized_label": "Label"})

    table_data = grouped[["Number of Tracks", "Label"]]
    table_data["Label"] = table_data["Label"].apply(lambda l: md_link(l, label_path(l, relative_to)))

    return table_data