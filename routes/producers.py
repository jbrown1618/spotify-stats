from data.repository import DataRepository
from routes.pagination import PRODUCER_SORT_COLUMNS, paginate_df


repository = DataRepository()


def producers_payload(filters: dict):
    producers = repository.producers_for_filters(filters)
    if producers.empty:
        return {"items": [], "total": 0}

    return paginate_df(producers, filters, PRODUCER_SORT_COLUMNS, "Most tracks")