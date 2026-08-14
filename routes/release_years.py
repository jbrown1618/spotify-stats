from data.repository import DataRepository
from routes.pagination import RELEASE_YEAR_SORT_COLUMNS, paginate_df


repository = DataRepository()


def release_years_payload(filters: dict):
    years = repository.release_year_track_counts_for_filters(filters)

    if years.empty:
        return {"items": [], "total": 0}

    return paginate_df(years, filters, RELEASE_YEAR_SORT_COLUMNS, "Newest")