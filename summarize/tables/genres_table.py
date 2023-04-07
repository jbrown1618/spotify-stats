import pandas as pd

from utils.util import md_link
from utils.path import genre_path

def genres_table(tracks: pd.DataFrame, track_genre: pd.DataFrame, relative_to: str):
    track_genre_subset = pd.merge(tracks[["track_uri", "track_liked"]], track_genre[["genre", "track_uri", "genre_has_page"]], on="track_uri")
    grouped = track_genre_subset.groupby("genre").agg({"track_uri": "count", "track_liked": "sum"}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "track_liked", "genre"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Tracks", "track_liked": "💚"})

    grouped["Genre"] = grouped["genre"].apply(lambda genre: display_genre(genre, track_genre, relative_to))

    return grouped[["Tracks", "💚", "Genre"]]

def display_genre(genre: str, track_genre: pd.DataFrame, relative_to: str):
    has_page = track_genre[track_genre["genre"] == genre].iloc[0]["genre_has_page"]

    return md_link(genre, genre_path(genre, relative_to)) if has_page else genre
