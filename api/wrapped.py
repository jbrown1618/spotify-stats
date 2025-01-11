import datetime

from api.utils import albums_by_artist, artists_by_album, artists_by_track
from data.provider import DataProvider
from data.raw import get_connection
from utils.json import to_json


def wrapped_payload(year):
    streams_by_track = track_streams(year)
    streams_by_album = album_streams(year)
    streams_by_artist = artist_streams(year)
    
    dp = DataProvider()
    tracks = dp.tracks(uris=set(streams_by_track.keys()))
    albums = dp.albums(uris=set(streams_by_album.keys()))
    artists = dp.artists(uris=set(streams_by_artist.keys()))
    
    return {
        "streams_by_track": streams_by_track,
        "streams_by_album": streams_by_album,
        "streams_by_artist": streams_by_artist,
        "tracks": to_json(tracks, 'track_uri'),
        "artists": to_json(artists, 'artist_uri'),
        "albums": to_json(albums, 'album_uri'),
        "artists_by_track": artists_by_track(tracks['track_uri']),
        "artists_by_album": artists_by_album(albums['album_uri']),
        "albums_by_artist": albums_by_artist(artists['artist_uri'])
    }


def track_streams(year: int, month: int = None):
    start, end = start_and_end(year, month)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT track_uri, SUM(h.stream_count) AS stream_count
            FROM listening_period p
            INNER JOIN listening_history h ON p.id = h.listening_period_id
            WHERE p.from_time >= %(start_time)s AND p.to_time < %(end_time)s
            GROUP BY h.track_uri
            ORDER BY SUM(h.stream_count) DESC
            LIMIT 100;
        """, {
            "start_time": start,
            "end_time": end
        })
        results = cursor.fetchall()

    out = {}
    for track_uri, stream_count in results:
        out[track_uri] = stream_count

    return out


def album_streams(year: int, month: int = None):
    start, end = start_and_end(year, month)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.album_uri, SUM(h.stream_count) AS stream_count
            FROM listening_period p
            INNER JOIN listening_history h ON p.id = h.listening_period_id
            INNER JOIN track t ON t.uri = h.track_uri
            WHERE p.from_time >= %(start_time)s AND p.to_time < %(end_time)s
            GROUP BY t.album_uri
            ORDER BY SUM(h.stream_count) DESC
            LIMIT 100;
        """, {
            "start_time": start,
            "end_time": end
        })
        results = cursor.fetchall()

    out = {}
    for album_uri, stream_count in results:
        out[album_uri] = stream_count

    return out
    

def artist_streams(year: int, month: int = None):
    start, end = start_and_end(year, month)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ta.artist_uri, SUM(h.stream_count) AS stream_count
            FROM listening_period p
            INNER JOIN listening_history h ON p.id = h.listening_period_id
            INNER JOIN track_artist ta ON ta.track_uri = h.track_uri
            WHERE p.from_time >= %(start_time)s AND p.to_time < %(end_time)s
            GROUP BY ta.artist_uri
            ORDER BY SUM(h.stream_count) DESC
            LIMIT 100;
        """, {
            "start_time": start,
            "end_time": end
        })
        results = cursor.fetchall()

    out = {}
    for artist_uri, stream_count in results:
        out[artist_uri] = stream_count

    return out


def start_and_end(year: int, month: int = None):
    start = datetime.datetime(year=year, month=month or 1, day=1)
    end = datetime.datetime(year=year + 1, month=1, day=1) if month is None \
        else datetime.datetime(year=year + 1, month=1, day=1) if month == 12 \
        else datetime.datetime(year=year, month=month + 1, day=1)

    return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))