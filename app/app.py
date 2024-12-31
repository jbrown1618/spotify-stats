import datetime
import json
import typing
import urllib
import pandas as pd
from flask import Flask, send_file, request

from data.provider import DataProvider
from data.raw import RawData
from data.sql.migrations.migrations import perform_all_migrations
from utils.ranking import album_ranks_over_time, artist_ranks_over_time, current_album_ranks, current_artist_ranks, current_track_ranks, track_ranks_over_time
from utils.util import first

pd.options.mode.chained_assignment = None  # default='warn'
app = Flask(__name__)


with app.app_context():
    perform_all_migrations()


@app.route("/")
def index():
    return send_file("./static/index.html")

# These values will only update when we refetch data, which is only once a day.
# Being a little out of date on these larger requests is fine in order to keep them fast.
__cache_no_filters = None
__cache_liked = None
__last_cached = None
cache_seconds = 60 * 60 * 6

@app.route("/api/summary")
def data():
    global __cache_no_filters
    global __cache_liked
    global __last_cached
    now = datetime.datetime.now()

    filters = to_filters(request.args)

    if is_empty_filter(filters) and __cache_no_filters is not None:
        if (now - __last_cached).seconds < cache_seconds:
            return __cache_no_filters
        else:
            __cache_no_filters = None
    
    if is_liked_filter(filters) and __cache_liked is not None:
        if (now - __last_cached).seconds < cache_seconds:
            return __cache_liked
        else:
            __cache_liked = None
    
    artist_uris = filters.get('artists', None)
    album_uris = filters.get('albums', None)
    playlist_uris = filters.get('playlists', None)
    label_names = filters.get('labels', None)
    genre_names = filters.get('genres', None)
    release_years = filters.get('years', None)
    liked = filters.get('liked', None)

    dp = DataProvider()


    tracks = dp.tracks(
        playlist_uris=playlist_uris, 
        artist_uris=artist_uris, 
        album_uris=album_uris,
        labels=label_names,
        genres=genre_names,
        years=release_years,
        liked=liked
    )

    playlists = dp.playlists(track_uris=tracks['track_uri'])
    artists = dp.artists(track_uris=tracks['track_uri'])
    albums = dp.albums(track_uris=tracks['track_uri'])
    genres = dp.genres(artist_uris=artists['artist_uri'])

    labels = dp.labels(
        label_names=label_names,
        album_uris=album_uris,
        artist_uris=artist_uris,
        playlist_uris=playlist_uris,
        years=release_years,
        liked=liked
    )

    summary_payload = {
        "playlists": to_json(playlists, 'playlist_uri'),
        "tracks": to_json(tracks, 'track_uri'),
        "artists": to_json(artists, 'artist_uri'),
        "albums": to_json(albums, 'album_uri'),
        "labels": [l for l in labels['album_standardized_label']],
        "genres": genres,
        "artists_by_track": artists_by_track(tracks),
        "artists_by_album": artists_by_album(albums),
        "albums_by_artist": albums_by_artist(artists),
        "playlist_track_counts": playlist_track_counts(playlists, tracks),
        "playlist_images": playlist_images(playlists),
        "artist_track_counts": artist_track_counts(artists, tracks),
        "track_rank_history": track_rank_history(tracks),
        "artist_rank_history": artist_rank_history(artists),
        "album_rank_history": album_rank_history(albums),
        "years": years(tracks),
        "filter_options": {
            "artists": to_json(artists[['artist_uri', 'artist_name']], 'artist_uri'),
            "albums": to_json(albums[['album_uri', 'album_name']], 'album_uri'),
            "playlists": to_json(playlists[['playlist_uri', 'playlist_name']], 'playlist_uri'),
            "labels": [l for l in labels['album_standardized_label']],
            "genres": dp.genres(artist_uris=artists['artist_uri']),
            "years": [y for y in albums['album_release_year'].unique()]
        },
    }

    if is_liked_filter(filters):
        __cache_liked = summary_payload
        __last_cached = now
    elif is_empty_filter(filters):
        __cache_no_filters = summary_payload
        __last_cached = now

    return summary_payload


def artists_by_track(tracks: pd.DataFrame):
    out = {}
    track_artist = RawData()['track_artist']
    for _, track in tracks.iterrows():
        artists = track_artist[track_artist['track_uri'] == track['track_uri']]
        uris = artists.sort_values(by="artist_index", ascending=True)['artist_uri']
        out[track['track_uri']] = [u for u in uris]
    return out


def albums_by_artist(artists: pd.DataFrame):
    out = {}
    album_artist = RawData()['album_artist']
    for _, artist in artists.iterrows():
        albums = album_artist[album_artist['artist_uri'] == artist['artist_uri']]
        uris = albums['album_uri']
        out[artist['artist_uri']] = [u for u in uris]
    return out


def artists_by_album(albums: pd.DataFrame):
    out = {}
    album_artist = RawData()['album_artist']
    for _, album in albums.iterrows():
        artists = album_artist[album_artist['album_uri'] == album['album_uri']]
        uris = artists['artist_uri']
        out[album['album_uri']] = [u for u in uris]
    return out


def playlist_track_counts(playlists, tracks):
    raw = RawData()
    playlist_track = raw['playlist_track']
    playlist_track = pd.merge(playlist_track, playlists, on="playlist_uri")
    playlist_track = pd.merge(playlist_track, tracks, on='track_uri')

    track_counts = playlist_track\
        .groupby("playlist_uri")\
        .agg({"track_uri": "count", "track_liked": "sum", "playlist_name": first})\
        .reset_index()\
        .rename(columns={"track_uri": "playlist_track_count", "track_liked": "playlist_liked_track_count"})
    
    return to_json(track_counts, 'playlist_uri')


# Now, the Spotify API does not always return playlist images. So we have to make them ourselves.
def playlist_images(playlists):
    out = {}

    raw = RawData()
    joined = pd.merge(raw['albums'], raw['tracks'], on='album_uri')
    playlist_track = raw['playlist_track']

    for _, playlist in playlists.iterrows():
        tracks = pd.merge(playlist_track[playlist_track['playlist_uri'] == playlist['playlist_uri']], joined, on='track_uri')
        grouped = tracks.groupby('album_image_url').agg({'track_uri': 'count'}).reset_index()
        top = grouped.sort_values('track_uri', ascending=False).head(4)
        out[playlist['playlist_uri']] = [url for url in top['album_image_url']]

    return out


def artist_track_counts(artists, tracks):
    raw = RawData()
    track_artist = raw['track_artist']
    track_artist = pd.merge(track_artist, artists, on="artist_uri")
    track_artist = pd.merge(track_artist, tracks, on='track_uri')

    track_counts = track_artist\
        .groupby("artist_uri")\
        .agg({"track_uri": "count", "track_liked": "sum", "artist_name": first})\
        .reset_index()\
        .rename(columns={"track_uri": "artist_track_count", "track_liked": "artist_liked_track_count"})
    
    return to_json(track_counts, 'artist_uri')


def track_rank_history(tracks):
    current_ranks = current_track_ranks(tracks['track_uri'])
    top_track_uris = current_ranks.sort_values('track_rank').head(10)['track_uri']
    ranks = track_ranks_over_time(top_track_uris)

    return to_json(ranks[['track_uri', 'track_rank', 'as_of_date']])


def artist_rank_history(artists):
    current_ranks = current_artist_ranks(artists['artist_uri'])
    top_track_uris = current_ranks.sort_values('artist_rank').head(10)['artist_uri']
    ranks = artist_ranks_over_time(top_track_uris)

    return to_json(ranks[['artist_uri', 'artist_rank', 'as_of_date']])


def album_rank_history(albums):
    current_ranks = current_album_ranks(albums['album_uri'])
    top_album_uris = current_ranks.sort_values('album_rank').head(10)['album_uri']
    ranks = album_ranks_over_time(top_album_uris)

    return to_json(ranks[['album_uri', 'album_rank', 'as_of_date']])


def years(tracks: pd.DataFrame):
    years_dict = {}
    for _, track in tracks.iterrows():
        year = track['album_release_year']
        liked = track['track_liked']

        if year in years_dict:
            years_dict[year]['total'] += 1
            if liked:
                years_dict[year]['liked'] += 1
        else:
            years_dict[year] = {
                'year': year,
                'total': 1,
                'liked': 1 if liked else 0
            }
    return years_dict


def is_empty_filter(filters):
    return len(filters) == 0


def is_liked_filter(filters):
    return len(filters) == 1 and "liked" in filters


array_filter_keys = ["artists", "albums", "playlists", "labels", "genres", "years"]
def to_filters(args: typing.Mapping[str, str]) -> typing.Mapping[str, typing.Iterable[str]]:
    filters = {
        key: to_array_filter(args.get(key, None))
        for key in array_filter_keys
        if args.get(key, None) is not None
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
