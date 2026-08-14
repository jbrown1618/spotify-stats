from data.repository import DataRepository
from routes.pagination import GENRE_SORT_COLUMNS, paginate_df


repository = DataRepository()


def genres_payload(filters: dict):
    genres = repository.genre_track_counts_for_filters(filters)

    if genres.empty:
        return {"items": [], "total": 0}

    genres = genres.rename(columns={
        'genre_track_count': 'track_count',
        'genre_total_track_count': 'total_track_count',
        'genre_liked_track_count': 'liked_track_count',
        'genre_total_liked_track_count': 'total_liked_track_count',
    })

    return paginate_df(genres, filters, GENRE_SORT_COLUMNS, "Most liked tracks")