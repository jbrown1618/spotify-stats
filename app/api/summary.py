
# These values will only update when we refetch data, which is only once a day.
# Being a little out of date on these larger requests is fine in order to keep them fast.
import datetime
import json
import typing

from flask import request
import pandas as pd
import urllib

from app.api.utils import albums_by_artist, artists_by_album, artists_by_track
from data.provider import DataProvider
from data.raw import get_connection
from utils.json import to_json
from utils.ranking import album_ranks_over_time, artist_ranks_over_time, current_album_ranks, current_artist_ranks, current_track_ranks, track_ranks_over_time


__cache_no_filters = None
__cache_liked = None
__last_cached = None
cache_seconds = 60 * 60 * 6

def summary_payload():
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
    labels = dp.labels(album_uris=albums['album_uri'])

    summary_payload = {
        "playlists": to_json(playlists, 'playlist_uri'),
        "tracks": to_json(tracks, 'track_uri'),
        "artists": to_json(artists, 'artist_uri'),
        "albums": to_json(albums, 'album_uri'),
        "artists_by_track": artists_by_track(tracks['track_uri']),
        "artists_by_album": artists_by_album(albums['album_uri']),
        "albums_by_artist": albums_by_artist(artists['artist_uri']),
        "playlist_track_counts": playlist_track_counts(tracks),
        "artist_track_counts": artist_track_counts(tracks),
        "label_track_counts": label_track_counts(tracks),
        "genre_track_counts": genre_track_counts(tracks),
        "track_rank_history": track_rank_history(tracks),
        "artist_rank_history": artist_rank_history(artists),
        "album_rank_history": album_rank_history(albums),
        "years": years(tracks),
        "filter_options": {
            "artists": to_json(artists[['artist_uri', 'artist_name']], 'artist_uri'),
            "albums": to_json(albums[['album_uri', 'album_name']], 'album_uri'),
            "playlists": to_json(playlists[['playlist_uri', 'playlist_name']], 'playlist_uri'),
            "labels": labels,
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


def playlist_track_counts(tracks: pd.DataFrame):
    if len(tracks) == 0:
        return {}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                pt.playlist_uri,
                p.name as playlist_name, 
                count(pt.track_uri) as playlist_track_count,
                count(lt.track_uri) as playlist_liked_track_count
            FROM playlist_track pt
                INNER JOIN playlist p ON p.uri = pt.playlist_uri
                LEFT JOIN liked_track lt ON lt.track_uri = pt.track_uri
            WHERE pt.track_uri in %(track_uris)s
            GROUP BY pt.playlist_uri, p.name
        """, { "track_uris": tuple(tracks['track_uri']) })
        result = cursor.fetchall()

    out = {}
    for playlist_uri, playlist_name, playlist_track_count, playlist_liked_track_count in result:
        out[playlist_uri] = {
            "playlist_uri": playlist_uri,
            "playlist_name": playlist_name,
            "playlist_track_count": playlist_track_count,
            "playlist_liked_track_count": playlist_liked_track_count
        }
    return out


def artist_track_counts(tracks):
    if len(tracks) == 0:
        return {}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                ta.artist_uri,
                a.name as artist_name, 
                count(ta.track_uri) as artist_track_count,
                count(lt.track_uri) as artist_liked_track_count
            FROM track_artist ta
                INNER JOIN artist a ON a.uri = ta.artist_uri
                LEFT JOIN liked_track lt ON lt.track_uri = ta.track_uri
            WHERE ta.track_uri in %(track_uris)s
            GROUP BY ta.artist_uri, a.name
        """, { "track_uris": tuple(tracks['track_uri']) })
        result = cursor.fetchall()

    out = {}
    for artist_uri, artist_name, artist_track_count, artist_liked_track_count in result:
        out[artist_uri] = {
            "artist_uri": artist_uri,
            "artist_name": artist_name,
            "artist_track_count": artist_track_count,
            "artist_liked_track_count": artist_liked_track_count
        }
    return out


def label_track_counts(tracks):
    if len(tracks) == 0:
        return {}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                rl.standardized_label as label, 
                count(t.uri) as label_track_count,
                count(lt.track_uri) as label_liked_track_count
            FROM record_label rl
                INNER JOIN track t ON t.album_uri = rl.album_uri
                LEFT JOIN liked_track lt ON lt.track_uri = t.uri
            WHERE t.uri in %(track_uris)s
            GROUP BY rl.standardized_label
        """, { "track_uris": tuple(tracks['track_uri']) })
        result = cursor.fetchall()

    out = {}
    for label, label_track_count, label_liked_track_count in result:
        out[label] = {
            "label": label,
            "label_track_count": label_track_count,
            "label_liked_track_count": label_liked_track_count
        }
    return out


def genre_track_counts(tracks):
    if len(tracks) == 0:
        return {}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                ag.genre, 
                count(ta.track_uri) as genre_track_count,
                count(lt.track_uri) as genre_liked_track_count
            FROM artist_genre ag
                INNER JOIN track_artist ta ON ag.artist_uri = ta.artist_uri
                LEFT JOIN liked_track lt ON ta.track_uri = lt.track_uri
            WHERE ta.track_uri in %(track_uris)s
            GROUP BY ag.genre
        """, { "track_uris": tuple(tracks['track_uri']) })
        result = cursor.fetchall()

    out = {}
    for genre, genre_track_count, genre_liked_track_count in result:
        out[genre] = {
            "genre": genre,
            "genre_track_count": genre_track_count,
            "genre_liked_track_count": genre_liked_track_count
        }
    return out


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
