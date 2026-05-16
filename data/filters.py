import json
import typing
from contextlib import contextmanager

import sqlalchemy

from data.query import query_text
from data.raw import get_engine
from routes.utils import to_date_range


def parse_request_args(args) -> dict:
    """Parse Flask request.args (query params) into the dict format payload functions expect.
    
    Array values are JSON-encoded strings in the query params.
    """
    result = {}
    array_keys = ['tracks', 'playlists', 'artists', 'albums', 'labels', 'genres', 'producers', 'years']
    for key in array_keys:
        val = args.get(key, None)
        if val is not None:
            result[key] = json.loads(val)
    
    if args.get('liked'):
        result['liked'] = True
    if args.get('wrapped'):
        result['wrapped'] = args.get('wrapped')
    if args.get('n'):
        result['n'] = int(args.get('n'))
    if args.get('sort'):
        result['sort'] = args.get('sort')
    if args.get('limit'):
        result['limit'] = int(args.get('limit'))
    if args.get('offset'):
        result['offset'] = int(args.get('offset'))
    
    return result


def parse_filters(request_json: dict) -> dict:
    """Parse a request JSON body into the standard filter parameter dict for SQL queries."""
    if request_json is None:
        request_json = {}

    min_stream_date, max_stream_date = to_date_range(request_json.get("wrapped"))

    tracks = request_json.get('tracks', None)
    playlists = request_json.get('playlists', None)
    artists = request_json.get('artists', None)
    albums = request_json.get('albums', None)
    labels = request_json.get('labels', None)
    genres = request_json.get('genres', None)
    producers = request_json.get('producers', None)
    years = request_json.get('years', None)
    liked = request_json.get('liked', None)

    return {
        "filter_tracks": tracks is not None,
        "track_uris": _to_tuple(tracks, 'EMPTY'),
        "liked": bool(liked),
        "filter_playlists": playlists is not None,
        "playlist_uris": _to_tuple(playlists, 'EMPTY'),
        "filter_artists": artists is not None,
        "artist_uris": _to_tuple(artists, 'EMPTY'),
        "filter_albums": albums is not None,
        "album_uris": _to_tuple(albums, 'EMPTY'),
        "filter_labels": labels is not None,
        "labels": _to_tuple(labels, 'EMPTY'),
        "filter_genres": genres is not None,
        "genres": _to_tuple(genres, 'EMPTY'),
        "filter_producers": producers is not None,
        "producers": _to_tuple(producers, 'EMPTY'),
        "filter_years": years is not None,
        "years": _to_tuple(years, 0),
        "wrapped_start_date": min_stream_date,
        "wrapped_end_date": max_stream_date,
    }


def create_matching_tracks_table(conn, params: dict):
    """Create the matching_track_uris temp table using a SQLAlchemy connection.
    
    Must be called within a connection context (e.g. `with engine.begin() as conn`).
    The temp table persists for the duration of that connection/transaction.
    """
    conn.execute(
        sqlalchemy.text(query_text('create_matching_track_uris')),
        params
    )


@contextmanager
def filtered_connection(filters: dict):
    """Context manager that yields a SQLAlchemy connection with matching_track_uris populated.
    
    Usage:
        with filtered_connection(request.json) as (conn, params):
            result = pd.read_sql_query(sqlalchemy.text(query), conn)
    """
    params = parse_filters(filters)
    with get_engine().begin() as conn:
        create_matching_tracks_table(conn, params)
        yield conn, params


def _to_tuple(value: typing.Optional[typing.Iterable], empty_sentinel) -> tuple:
    if value is None or len(value) == 0:
        return (empty_sentinel,)
    return tuple(value)

