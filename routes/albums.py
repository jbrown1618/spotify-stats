import typing

from routes.utils import to_json
from data.provider import DataProvider


def albums_payload(track_uris: typing.Iterable[str]):
    if track_uris is None or len(track_uris) == 0:
        return {}
    dp = DataProvider()
    albums = dp.albums(track_uris=track_uris)
    return to_json(albums, 'album_uri')