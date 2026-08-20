from data.repository import DataRepository
from routes.pagination import ALBUM_SORT_COLUMNS, paginate_df
from routes.utils import to_json


repository = DataRepository()


def albums_payload(filters: dict):
    albums = repository.albums_for_filters(filters)
    if albums.empty:
        return {"items": [], "total": 0}

    return paginate_df(albums, filters, ALBUM_SORT_COLUMNS, "Most streams")


def album_metadata_payload(album_uri: str):
    metadata = repository.album_metadata(album_uri)
    return {
        "discogs_masters": to_json(metadata.discogs_masters),
        "tracks": to_json(metadata.tracks),
    }