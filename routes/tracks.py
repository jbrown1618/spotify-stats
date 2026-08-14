import typing

from data.repository import DataRepository
from routes.pagination import TRACK_SORT_COLUMNS, paginate_df
from routes.utils import to_json


repository = DataRepository()


def tracks_search_payload(filters: typing.Mapping[str, str]):
    tracks = repository.tracks_for_filters(filters)
    return paginate_df(tracks, filters, TRACK_SORT_COLUMNS, "Most streams")


def top_tracks(from_date, to_date):
    return repository.top_track_uris(from_date, to_date)


def track_credits_payload(track_uri):
    return to_json(repository.track_credits(track_uri))