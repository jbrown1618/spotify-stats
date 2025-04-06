import typing

from routes.utils import to_json
from data.provider import DataProvider


def playlists_payload(track_uris: typing.Iterable[str]):
    dp = DataProvider()
    playlists = dp.playlists(track_uris=track_uris)
    return to_json(playlists, 'playlist_uri')