import typing
from data.raw import get_connection


def artists_by_track(track_uris: typing.Iterable[str]):
    if len(track_uris) == 0: return {}

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT track_uri, array_agg(artist_uri)
            FROM track_artist
            WHERE track_uri in %(track_uris)s
            GROUP BY track_uri
        """, { "track_uris": tuple(track_uris) })
        result = cursor.fetchall()

    out = {}
    for track_uri, artist_uris in result:
        out[track_uri] = artist_uris
    return out


def albums_by_artist(artist_uris: typing.Iterable[str]):
    if len(artist_uris) == 0: return {}

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ta.artist_uri, array_agg(t.album_uri)
            FROM track_artist ta
                INNER JOIN track t ON t.uri = ta.track_uri
            WHERE ta.artist_uri in %(artist_uris)s
            GROUP BY ta.artist_uri
        """, { "artist_uris": tuple(artist_uris) })
        result = cursor.fetchall()

    out = {}
    for artist_uri, album_uris in result:
        out[artist_uri] = list(set(album_uris))
    return out


def artists_by_album(album_uris: typing.Iterable[str]):
    if len(album_uris) == 0: return {}

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT album_uri, array_agg(artist_uri)
            FROM album_artist
            WHERE album_uri in %(album_uris)s
            GROUP BY album_uri
        """, { "album_uris": tuple(album_uris) })
        result = cursor.fetchall()

    out = {}
    for album_uri, artist_uris in result:
        out[album_uri] = artist_uris
    return out