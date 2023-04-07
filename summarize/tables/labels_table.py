import pandas as pd

from utils.util import first, md_link
from utils.path import label_path

def labels_table(tracks: pd.DataFrame, album_record_label: pd.DataFrame, relative_to: str):
    labels_by_page = album_record_label.groupby("album_standardized_label").agg({"label_has_page": first}).reset_index()
    labels_with_summary = set(labels_by_page[labels_by_page["label_has_page"]]["album_standardized_label"])

    grouped = pd.merge(tracks, album_record_label, on="album_uri").groupby("album_standardized_label").agg({"track_uri": "count", "track_liked": "sum"}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "track_liked", "album_standardized_label"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Tracks", "track_liked": "💚", "album_standardized_label": "Label"})

    table_data = grouped[["Tracks", "💚", "Label"]]
    table_data["Label"] = table_data["Label"].apply(lambda l:  md_link(l, label_path(l, relative_to)) if l in labels_with_summary else l)

    return table_data
