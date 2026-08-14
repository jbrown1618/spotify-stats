from data.repository import DataRepository
from routes.utils import to_json


repository = DataRepository()


def artist_stream_share_by_month_payload(filters: dict):
    n = filters.get("n", 10)
    rows = repository.artist_stream_share_by_month(filters, n)
    return to_json(rows)


def genre_stream_share_by_month_payload(filters: dict):
    n = filters.get("n", 10)
    rows = repository.genre_stream_share_by_month(filters, n)
    return to_json(rows)
