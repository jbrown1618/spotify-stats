from data.repository import DataRepository
from routes.pagination import PLAYLIST_SORT_COLUMNS, paginate_df


repository = DataRepository()


def playlists_payload(filters: dict):
    playlists = repository.playlists_for_filters(filters)
    if playlists.empty:
        return {"items": [], "total": 0}

    return paginate_df(playlists, filters, PLAYLIST_SORT_COLUMNS, "Most liked tracks")