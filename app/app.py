import json
import typing
import urllib
import pandas as pd
from flask import Flask, send_file, request

from data.provider import DataProvider
from data.raw import RawData
from utils.ranking import album_ranks_over_time, artist_ranks_over_time, track_ranks_over_time
from utils.util import first

pd.options.mode.chained_assignment = None  # default='warn'
app = Flask(__name__)


@app.route("/")
def index():
    return send_file("./static/index.html")


@app.route("/api/summary")
def data():
    dp = DataProvider()

    filters = to_filters(request.args)
    artist_uris = filters.get('artists', None)
    album_uris = filters.get('albums', None)
    playlist_uris = filters.get('playlists', None)
    labels = filters.get('labels', None)
    genres = filters.get('genres', None)
    liked = filters.get('liked', None)

    playlists = dp.playlists(
        uris=playlist_uris, 
        artist_uris=artist_uris,
        album_uris=album_uris,
        labels=labels,
        genres=genres
    )

    tracks = dp.tracks(
        playlist_uris=playlist_uris, 
        artist_uris=artist_uris, 
        album_uris=album_uris,
        labels=labels,
        genres=genres,
        liked=liked
    )

    artists = dp.artists(
        uris=artist_uris,
        album_uris=album_uris,
        playlist_uris=playlist_uris,
        labels=labels,
        genres=genres,
        with_liked_tracks=liked
    )
    
    albums = dp.albums(
        uris=album_uris,
        artist_uris=artist_uris,
        playlist_uris=playlist_uris,
        labels=labels,
        genres=genres
    )

    labels = dp.labels(
        label_names=labels,
        album_uris=album_uris,
        artist_uris=artist_uris,
        playlist_uris=playlist_uris,
        liked=liked
    )

    genres = dp.genres(
        names=genres,
        playlist_uris=playlist_uris,
        artist_uris=artist_uris,
        album_uris=album_uris,
        labels=labels,
        with_liked_tracks=liked
    )

    return {
        "filter_options": get_filter_options(filters),
        "playlists": to_json(playlists, 'playlist_uri'),
        "tracks": to_json(tracks, 'track_uri'),
        "artists": to_json(artists, 'artist_uri'),
        "albums": to_json(albums, 'album_uri'),
        "labels": [l for l in labels['album_standardized_label']],
        "genres": [g for g in genres],
        "playlist_track_counts": playlist_track_counts(playlists, tracks),
        "track_rank_history": track_rank_history(tracks),
        "artist_rank_history": artist_rank_history(artists),
        "album_rank_history": album_rank_history(albums)
    }


def get_filter_options(filters):
    dp = DataProvider()
    artist_uris = filters.get('artists', None)
    album_uris = filters.get('albums', None)
    playlist_uris = filters.get('playlists', None)
    labels = filters.get('labels', None)
    genres = filters.get('genres', None)
    liked = filters.get('liked', None)

    return {
        "artists": to_json(dp.artists(
            album_uris=album_uris, 
            playlist_uris=playlist_uris,
            labels=labels,
            genres=genres,
            with_liked_tracks=liked
        )[['artist_uri', 'artist_name']], 'artist_uri'),
        "albums": to_json(dp.albums(
            artist_uris=artist_uris, 
            playlist_uris=playlist_uris,
            labels=labels,
            genres=genres
        )[['album_uri', 'album_name']], 'album_uri'),
        "playlists": to_json(dp.playlists(
            artist_uris=artist_uris, 
            album_uris=album_uris,
            labels=labels,
            genres=genres
        )[['playlist_uri', 'playlist_name']], 'playlist_uri'),
        "labels": [l for l in dp.labels(
            album_uris=album_uris,
            artist_uris=artist_uris,
            playlist_uris=playlist_uris,
            genres=genres,
            liked=liked
        )['album_standardized_label']],
        "genres": [g for g in dp.genres(
            playlist_uris=playlist_uris,
            artist_uris=artist_uris,
            album_uris=album_uris,
            labels=labels,
            with_liked_tracks=liked
        )]
    }


def playlist_track_counts(playlists, tracks):
    raw = RawData()
    playlist_track = raw['playlist_track']
    playlist_track = pd.merge(playlist_track, playlists, on="playlist_uri")
    playlist_track = pd.merge(playlist_track, tracks, on='track_uri')

    track_counts = playlist_track\
        .groupby("playlist_uri")\
        .agg({"track_uri": "count", "track_liked": "sum", "playlist_name": first})\
        .reset_index()\
        .rename(columns={"track_uri": "playlist_track_count", "track_liked": "playlist_track_liked_count"})
    
    return to_json(track_counts, 'playlist_uri')


def track_rank_history(tracks):
    ranks = track_ranks_over_time()
    ranks = ranks[ranks['track_uri'].isin(tracks['track_uri'])]

    max_date = ranks['as_of_date'].max()
    current_top_tracks = ranks[
        (ranks['as_of_date'] == max_date)
    ].head(10)['track_uri']

    ranks = ranks[ranks['track_uri'].isin(current_top_tracks)]

    return to_json(ranks[['track_uri', 'track_rank', 'as_of_date']])


def artist_rank_history(artists):
    ranks = artist_ranks_over_time()
    ranks = ranks[ranks['artist_uri'].isin(artists['artist_uri'])]

    max_date = ranks['as_of_date'].max()
    current_top_artists = ranks[
        (ranks['as_of_date'] == max_date)
    ].head(10)['artist_uri']

    ranks = ranks[ranks['artist_uri'].isin(current_top_artists)]

    return to_json(ranks[['artist_uri', 'artist_rank', 'as_of_date']])


def album_rank_history(albums):
    ranks = album_ranks_over_time()
    ranks = ranks[ranks['album_uri'].isin(albums['album_uri'])]

    max_date = ranks['as_of_date'].max()
    current_top_albums = ranks[
        (ranks['as_of_date'] == max_date)
    ].head(10)['album_uri']

    ranks = ranks[ranks['album_uri'].isin(current_top_albums)]

    return to_json(ranks[['album_uri', 'album_rank', 'as_of_date']])


array_filter_keys = ["artists", "albums", "playlists", "labels", "genres"]
def to_filters(args: typing.Mapping[str, str]) -> typing.Mapping[str, typing.Iterable[str]]:
    filters = {
        key: to_array_filter(args.get(key, None))
        for key in array_filter_keys
    }

    liked = args.get("liked", None)
    if liked is not None:
        liked = liked.lower() == "true"
    filters["liked"] = liked

    return filters


def to_array_filter(arg: str) -> typing.Iterable[str]:
    if arg is None:
        return None
    
    return json.loads(urllib.parse.unquote(arg))


def to_json(df: pd.DataFrame, col: str = None):
    if col is not None:
        index_col = col + '__index'
        df[index_col] = df[col].copy()
        df = df.set_index(index_col)
        return json.loads(df.to_json(orient="index"))
    
    return json.loads(df.to_json(orient="records", index=True))
