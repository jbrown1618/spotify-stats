import pandas as pd

from data.provider import DataProvider
from utils.util import md_link
from utils.path import label_overview_path

def labels_table(tracks: pd.DataFrame, relative_to: str):
    dp = DataProvider()

    labels = dp.labels(track_uris=tracks["track_uri"])\
        .sort_values(by=["track_liked_count", "track_count", "album_standardized_label"], ascending=False)\
        .rename(columns={"track_count": "Tracks", "track_liked_count": "💚"})
    
    if len(labels) == 0:
        return None

    labels["Label"] = labels.apply(lambda l: display_label(l, relative_to), axis=1)
    table_data = labels[["Tracks", "💚", "Label"]]

    return table_data


def display_label(label: pd.Series, relative_to: str):
    label_name = label['album_standardized_label']
    if label['label_has_page']:
        return md_link(label_name, label_overview_path(label_name, relative_to))
    
    return label_name