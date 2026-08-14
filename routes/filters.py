import pandas as pd
import sqlalchemy

from data.filters import filtered_connection
from data.query import query_text
from routes.utils import to_json


def filter_options_payload():
    with filtered_connection({"liked": True}) as (conn, params):
        playlists = pd.read_sql_query(
            sqlalchemy.text(query_text("select_playlists")),
            conn,
        )
        artists = pd.read_sql_query(
            sqlalchemy.text(query_text("select_artists")),
            conn,
            params={
                "filter_artists": False,
                "artist_uris": ("EMPTY",),
                "filter_mbids": False,
                "mbids": ("EMPTY",),
                "wrapped_start_date": params["wrapped_start_date"],
                "wrapped_end_date": params["wrapped_end_date"],
            },
        )
        albums = pd.read_sql_query(
            sqlalchemy.text(query_text("select_albums")),
            conn,
            params={
                "wrapped_start_date": params["wrapped_start_date"],
                "wrapped_end_date": params["wrapped_end_date"],
            },
        )
        producers = pd.read_sql_query(
            sqlalchemy.text(query_text("select_producers")),
            conn,
        ).drop_duplicates(subset=["producer_mbid"], keep="first")
        labels = pd.read_sql_query(
            sqlalchemy.text(query_text("select_labels")),
            conn,
            params={
                "filter_albums": True,
                "album_uris": _to_tuple(albums["album_uri"], "EMPTY"),
            },
        )["standardized_label"].to_list()
        genres = pd.read_sql_query(
            sqlalchemy.text(query_text("select_genres")),
            conn,
            params={
                "filter_artists": True,
                "artist_uris": _to_tuple(artists["artist_uri"], "EMPTY"),
            },
        )["genre"].to_list()

    return {
        "artists": to_json(
            artists[["artist_uri", "artist_name"]],
            "artist_uri",
        ),
        "albums": to_json(albums[["album_uri", "album_name"]], "album_uri"),
        "playlists": to_json(
            playlists[["playlist_uri", "playlist_name"]],
            "playlist_uri",
        ),
        "producers": to_json(
            producers[["producer_name", "producer_mbid"]],
            "producer_mbid",
        ),
        "labels": labels,
        "genres": genres,
        "years": [year for year in albums["album_release_year"].unique()],
    }


def _to_tuple(values, empty_sentinel):
    if values.empty:
        return (empty_sentinel,)
    return tuple(values)