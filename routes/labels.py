from data.repository import DataRepository
from routes.pagination import LABEL_SORT_COLUMNS, paginate_df


repository = DataRepository()


def labels_payload(filters: dict):
    labels = repository.label_track_counts_for_filters(filters)

    if labels.empty:
        return {"items": [], "total": 0}

    labels = labels.rename(columns={
        'label_track_count': 'track_count',
        'label_total_track_count': 'total_track_count',
        'label_liked_track_count': 'liked_track_count',
        'label_total_liked_track_count': 'total_liked_track_count',
    })

    return paginate_df(labels, filters, LABEL_SORT_COLUMNS, "Most liked tracks")