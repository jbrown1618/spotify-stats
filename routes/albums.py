from data.repository import DataRepository
from routes.pagination import ALBUM_SORT_COLUMNS, paginate_df


repository = DataRepository()


def albums_payload(filters: dict):
    albums = repository.albums_for_filters(filters)
    if albums.empty:
        return {"items": [], "total": 0}

    return paginate_df(albums, filters, ALBUM_SORT_COLUMNS, "Most streams")