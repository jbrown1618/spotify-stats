from data.repository import DataRepository
from routes.pagination import PRODUCER_SORT_COLUMNS, paginate_df
from routes.utils import to_json


repository = DataRepository()


def producers_payload(filters: dict):
    producers = repository.producers_for_filters(filters)
    if producers.empty:
        return {"items": [], "total": 0}

    return paginate_df(producers, filters, PRODUCER_SORT_COLUMNS, "Most tracks")


def producer_profile_payload(producer_key: str):
    profiles = repository.producer_profile(producer_key)
    if profiles.empty:
        return {}
    return to_json(profiles)[0]
