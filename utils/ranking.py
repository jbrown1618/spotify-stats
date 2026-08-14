import typing

from data.repository import DataRepository


repository = DataRepository()


def track_ranks_over_time(track_uris: typing.Iterable[str], from_date, to_date):
    return repository.track_ranks_over_time(track_uris, from_date, to_date)


def artist_ranks_over_time(artist_uris: typing.Iterable[str], from_date, to_date):
    return repository.artist_ranks_over_time(artist_uris, from_date, to_date)


def album_ranks_over_time(album_uris: typing.Iterable[str], from_date, to_date):
    return repository.album_ranks_over_time(album_uris, from_date, to_date)


def track_streams_by_month(track_uris, from_date, to_date):
    return repository.track_streams_by_month(track_uris, from_date, to_date)


def artist_streams_by_month(artist_uris, from_date, to_date):
    return repository.artist_streams_by_month(artist_uris, from_date, to_date)


def album_streams_by_month(album_uris, from_date, to_date):
    return repository.album_streams_by_month(album_uris, from_date, to_date)

def filtered_track_ranks_over_time(filters: dict, n: int = 10):
    return repository.filtered_track_ranks_over_time(filters, n)


def filtered_track_streams_by_month(filters: dict, n: int = 5):
    return repository.filtered_track_streams_by_month(filters, n)


def filtered_artist_ranks_over_time(filters: dict, n: int = 10):
    return repository.filtered_artist_ranks_over_time(filters, n)


def filtered_artist_streams_by_month(filters: dict, n: int = 5):
    return repository.filtered_artist_streams_by_month(filters, n)


def filtered_album_ranks_over_time(filters: dict, n: int = 10):
    return repository.filtered_album_ranks_over_time(filters, n)


def filtered_album_streams_by_month(filters: dict, n: int = 5):
    return repository.filtered_album_streams_by_month(filters, n)
