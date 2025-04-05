

# These values will only update when we refetch data, which is only once a day.
# Being a little out of date on these larger requests is fine in order to keep them fast.
import datetime

from flask import request
import pandas as pd
import sqlalchemy

from app.utils import is_empty_filter, is_liked_filter, to_filters, to_json
from data.provider import DataProvider
from data.query import query_text
from data.raw import get_connection, get_engine
from utils.ranking import album_ranks_over_time, artist_ranks_over_time, current_album_ranks, current_track_ranks, track_ranks_over_time


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

    min_stream_date = filters.get('min_stream_date', None)
    max_stream_date = filters.get('max_stream_date', None)

    streams_by_track = None

    track_uris = None
    if min_stream_date is not None and max_stream_date is not None:
        streams_by_track = track_streams(min_stream_date, max_stream_date)
        track_uris = streams_by_track['track_uri']

    dp = DataProvider()

    tracks = dp.tracks(
        uris=track_uris,
        playlist_uris=playlist_uris, 
        artist_uris=artist_uris, 
        album_uris=album_uris,
        labels=label_names,
        genres=genre_names,
        years=release_years,
        liked=liked
    )

    if streams_by_track is None:
        streams_by_track = current_track_ranks(tracks['track_uri'])[['track_uri', 'track_rank', 'track_stream_count']]

    playlists = dp.playlists(track_uris=tracks['track_uri'])
    artists = dp.artists(track_uris=tracks['track_uri'])
    albums = dp.albums(track_uris=tracks['track_uri'])
    labels = dp.labels(album_uris=albums['album_uri'])

    summary_payload = {
        "playlists": to_json(playlists, 'playlist_uri'),
        "tracks": to_json(tracks, 'track_uri'),
        "artists": to_json(artists, 'artist_uri'),
        "albums": to_json(albums, 'album_uri'),
        "artists_by_track": artists_by_track(tracks),
        "artists_by_album": artists_by_album(albums),
        "albums_by_artist": albums_by_artist(artists),
        "playlist_track_counts": playlist_track_counts(tracks),
        "artist_track_counts": artist_track_counts(tracks),
        "label_track_counts": label_track_counts(tracks),
        "genre_track_counts": genre_track_counts(tracks),
        "years": years(tracks),
        # No equivalent API yet
        "track_rank_history": track_rank_history(tracks, min_stream_date, max_stream_date),
        "artist_rank_history": artist_rank_history(artists, min_stream_date, max_stream_date),
        "album_rank_history": album_rank_history(albums, min_stream_date, max_stream_date),
        "streams_by_track": to_json(streams_by_track, 'track_uri'),
        "streams_by_month": overall_streams_by_month(tracks, min_stream_date, max_stream_date),
        "track_streams_by_month": track_streams_by_month(tracks, min_stream_date, max_stream_date),
        "artist_streams_by_month": artist_streams_by_month(artists, min_stream_date, max_stream_date),
        "album_streams_by_month": album_streams_by_month(albums, min_stream_date, max_stream_date),
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


def artists_by_track(tracks: pd.DataFrame):
    if len(tracks) == 0: return {}

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_artists_by_track'), 
            { "track_uris": tuple(tracks['track_uri']) }
        )
        result = cursor.fetchall()

    out = {}
    for track_uri, artist_uris in result:
        out[track_uri] = artist_uris
    return out


def albums_by_artist(artists: pd.DataFrame):
    if len(artists) == 0: return {}

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_albums_by_artist'), 
            { "artist_uris": tuple(artists['artist_uri']) }
        )
        result = cursor.fetchall()

    out = {}
    for artist_uri, album_uris in result:
        out[artist_uri] = list(set(album_uris))
    return out


def artists_by_album(albums: pd.DataFrame):
    if len(albums) == 0: return {}

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_artists_by_album'), 
            { "album_uris": tuple(albums['album_uri']) }
        )
        result = cursor.fetchall()

    out = {}
    for album_uri, artist_uris in result:
        out[album_uri] = artist_uris
    return out


def playlist_track_counts(tracks: pd.DataFrame):
    if len(tracks) == 0:
        return {}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_playlist_track_counts'), 
            { "track_uris": tuple(tracks['track_uri']) }
        )
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
        cursor.execute(
            query_text('select_artist_track_counts'), 
            { "track_uris": tuple(tracks['track_uri']) }
        )
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
        cursor.execute(
            query_text('select_label_track_counts'), 
            { "track_uris": tuple(tracks['track_uri']) }
        )
        result = cursor.fetchall()

    out = {}
    for label, track_count, _, liked_track_count, _ in result:
        out[label] = {
            "label": label,
            "label_track_count": track_count,
            "label_liked_track_count": liked_track_count
        }
    return out


def genre_track_counts(tracks):
    if len(tracks) == 0:
        return {}
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_genre_track_counts'), 
            { "track_uris": tuple(tracks['track_uri']) }
        )
        result = cursor.fetchall()

    out = {}
    for genre, track_count, _, liked_track_count, _ in result:
        out[genre] = {
            "genre": genre,
            "genre_track_count": track_count,
            "genre_liked_track_count": liked_track_count
        }
    return out


def track_rank_history(tracks, from_date, to_date):
    current_ranks = current_track_ranks(tracks['track_uri'])
    top_track_uris = current_ranks.sort_values('track_rank', ascending=True).head(10)['track_uri']
    ranks = track_ranks_over_time(top_track_uris, from_date, to_date)

    return to_json(ranks[['track_uri', 'track_rank', 'track_stream_count', 'as_of_date']])


def track_streams(from_date, to_date):
    with get_engine().begin() as conn:
        return pd.read_sql_query(
            sqlalchemy.text(query_text('select_top_tracks_for_date_range')), 
            conn, 
            params={ 'min_stream_date': from_date, 'max_stream_date': to_date }
        )[['track_uri', 'track_rank', 'track_stream_count']]


def track_streams_by_month(tracks, from_date, to_date):
    top_track_uris = tracks.sort_values('track_rank').head(5)['track_uri']
    top_track_uris = tuple(top_track_uris) if len(top_track_uris) > 0 else tuple(['EMPTY'])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_track_streams_by_month'), 
            {
                "track_uris": top_track_uris,
                "from_date": from_date,
                "to_date": to_date
            }
        )
        results = cursor.fetchall()

    out = {}
    for track_uri, year, month, stream_count in results:
        year = int(year)
        month = int(month)
        if track_uri not in out:
            out[track_uri] = {}
        if year not in out[track_uri]:
            out[track_uri][year] = {}
        if month not in out[track_uri][year]:
            out[track_uri][year][month] = stream_count
    return out


def artist_rank_history(artists, from_date, to_date):
    top_artist_uris = artists.sort_values('artist_rank').head(10)['artist_uri']
    ranks = artist_ranks_over_time(top_artist_uris, from_date, to_date)

    return to_json(ranks[['artist_uri', 'artist_rank', 'artist_stream_count', 'as_of_date']])


def artist_streams_by_month(artists, from_date, to_date):
    top_artist_uris = artists.sort_values('artist_rank').head(5)['artist_uri']
    top_artist_uris = tuple(top_artist_uris) if len(top_artist_uris) > 0 else tuple(['EMPTY'])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_artist_streams_by_month'),
            {
                "artist_uris": top_artist_uris,
                "from_date": from_date,
                "to_date": to_date
            }
        )
        results = cursor.fetchall()

    out = {}
    for artist_uri, year, month, stream_count in results:
        year = int(year)
        month = int(month)
        if artist_uri not in out:
            out[artist_uri] = {}
        if year not in out[artist_uri]:
            out[artist_uri][year] = {}
        if month not in out[artist_uri][year]:
            out[artist_uri][year][month] = stream_count
    return out


def album_rank_history(albums, from_date, to_date):
    current_ranks = current_album_ranks(albums['album_uri'])
    top_album_uris = current_ranks.sort_values('album_rank').head(10)['album_uri']
    ranks = album_ranks_over_time(top_album_uris, from_date, to_date)

    return to_json(ranks[['album_uri', 'album_rank', 'album_stream_count', 'as_of_date']])


def album_streams_by_month(albums, from_date, to_date):
    top_album_uris = albums.sort_values('album_rank').head(5)['album_uri']
    top_album_uris = tuple(top_album_uris) if len(top_album_uris) > 0 else tuple(['EMPTY'])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_album_streams_by_month'),
            {
                "album_uris": top_album_uris,
                "from_date": from_date,
                "to_date": to_date
            }
        )
        results = cursor.fetchall()

    out = {}
    for album_uri, year, month, stream_count in results:
        year = int(year)
        month = int(month)
        if album_uri not in out:
            out[album_uri] = {}
        if year not in out[album_uri]:
            out[album_uri][year] = {}
        if month not in out[album_uri][year]:
            out[album_uri][year][month] = stream_count
    return out


def overall_streams_by_month(tracks, from_date, to_date):
    track_uris = tracks['track_uri']
    track_uris = tuple(track_uris) if len(track_uris) > 0 else tuple(['EMPTY'])
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            query_text('select_overall_streams_by_month'),
            {
                "track_uris": track_uris,
                "from_date": from_date,
                "to_date": to_date
            }
        )
        results = cursor.fetchall()

    out = {}
    for year, month, stream_count in results:
        year = int(year)
        month = int(month)
        if year not in out:
            out[year] = {}
        if month not in out[year]:
            out[year][month] = stream_count
    return out


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