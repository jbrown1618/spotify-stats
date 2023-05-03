import pandas as pd

from data.provider import DataProvider
from utils.util import md_link
from utils.path import genre_overview_path

def genres_table(tracks: pd.DataFrame, relative_to: str):
    dp = DataProvider()
    track_genre_subset = pd.merge(tracks[["track_uri", "track_liked"]], dp.track_genre(), on="track_uri")
    grouped = track_genre_subset.groupby("genre").agg({"track_uri": "count", "track_liked": "sum"}).reset_index()
    grouped = grouped.sort_values(by=["track_liked", "track_uri", "genre"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Tracks", "track_liked": "💚"})

    grouped["Genre"] = grouped["genre"].apply(lambda genre: display_genre(genre, relative_to))

    return grouped[["Tracks", "💚", "Genre"]]


def display_genre(genre: str, relative_to: str):
    dp = DataProvider()
    track_genre = dp.track_genre()
    has_page = track_genre[track_genre["genre"] == genre].iloc[0]["genre_has_page"]

    return md_link(genre, genre_overview_path(genre, relative_to)) if has_page else genre
