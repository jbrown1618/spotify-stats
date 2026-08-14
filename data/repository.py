from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import pandas as pd
import sqlalchemy

from data.database import get_connection, get_engine
from data.filters import filtered_connection, parse_filters
from data.query import query_text


@dataclass(frozen=True)
class ArtistCredits:
    credits: pd.DataFrame
    relationships: pd.DataFrame


@dataclass(frozen=True)
class FilterOptions:
    playlists: pd.DataFrame
    artists: pd.DataFrame
    albums: pd.DataFrame
    producers: pd.DataFrame
    labels: pd.DataFrame
    genres: pd.DataFrame


@dataclass(frozen=True)
class QueuedJob:
    id: int
    type: str
    arguments: str


@dataclass(frozen=True)
class TrackRecommendations:
    matching_track_count: int | None
    tracks: pd.DataFrame | None


class StreamWriter:
    def __init__(self, cursor):
        self._cursor = cursor

    def add(self, track_uri: str, played_at: float) -> None:
        self._cursor.execute(
            query_text("insert_stream"),
            {"track_uri": track_uri, "played_at": played_at},
        )


class DataRepository:
    """Stateless, method-based boundary for application database queries."""

    def tracks_for_filters(self, filters: Mapping[str, Any]) -> pd.DataFrame:
        return self._filtered_dataframe(
            filters,
            "select_filtered_tracks",
            lambda params: self._wrapped_date_params(params),
        )

    def albums_for_filters(self, filters: Mapping[str, Any]) -> pd.DataFrame:
        return self._filtered_dataframe(
            filters,
            "select_albums",
            lambda params: self._wrapped_date_params(params),
        )

    def artists_for_filters(self, filters: Mapping[str, Any]) -> pd.DataFrame:
        return self._filtered_dataframe(
            filters,
            "select_artists",
            lambda params: {
                "filter_artists": False,
                "artist_uris": ("EMPTY",),
                "filter_mbids": False,
                "mbids": ("EMPTY",),
                **self._wrapped_date_params(params),
            },
        )

    def playlists_for_filters(self, filters: Mapping[str, Any]) -> pd.DataFrame:
        return self._filtered_dataframe(filters, "select_playlists")

    def producers_for_filters(self, filters: Mapping[str, Any]) -> pd.DataFrame:
        return self._filtered_dataframe(filters, "select_producers")

    def genre_track_counts_for_filters(
        self, filters: Mapping[str, Any]
    ) -> pd.DataFrame:
        return self._filtered_dataframe(filters, "select_genre_track_counts")

    def label_track_counts_for_filters(
        self, filters: Mapping[str, Any]
    ) -> pd.DataFrame:
        return self._filtered_dataframe(filters, "select_label_track_counts")

    def release_year_track_counts_for_filters(
        self, filters: Mapping[str, Any]
    ) -> pd.DataFrame:
        return self._filtered_dataframe(filters, "select_release_year_track_counts")

    def filter_options(self) -> FilterOptions:
        with filtered_connection({"liked": True}) as (connection, params):
            playlists = self._read_dataframe_on(
                connection,
                "select_playlists",
            )
            artists = self._read_dataframe_on(
                connection,
                "select_artists",
                {
                    "filter_artists": False,
                    "artist_uris": ("EMPTY",),
                    "filter_mbids": False,
                    "mbids": ("EMPTY",),
                    **self._wrapped_date_params(params),
                },
            )
            albums = self._read_dataframe_on(
                connection,
                "select_albums",
                self._wrapped_date_params(params),
            )
            producers = self._read_dataframe_on(
                connection,
                "select_producers",
            )
            labels = self._read_dataframe_on(
                connection,
                "select_labels",
                {
                    "filter_albums": True,
                    "album_uris": self._values_or_sentinel(
                        albums["album_uri"], "EMPTY"
                    ),
                },
            )
            genres = self._read_dataframe_on(
                connection,
                "select_genres",
                {
                    "filter_artists": True,
                    "artist_uris": self._values_or_sentinel(
                        artists["artist_uri"], "EMPTY"
                    ),
                },
            )

        return FilterOptions(
            playlists=playlists,
            artists=artists,
            albums=albums,
            producers=producers,
            labels=labels,
            genres=genres,
        )

    def artist_credits(self, artist_uri: str) -> ArtistCredits:
        with get_engine().begin() as connection:
            credits = self._read_dataframe_on(
                connection,
                "select_artist_credits",
                {"artist_uri": artist_uri},
            )
            relationships = self._read_dataframe_on(
                connection,
                "select_artist_relationships",
                {"artist_uri": artist_uri},
            )
        return ArtistCredits(credits=credits, relationships=relationships)

    def track_credits(self, track_uri: str) -> pd.DataFrame:
        return self._read_dataframe(
            "select_track_credits",
            {"track_uri": track_uri},
        )

    def top_track_uris(self, from_date, to_date) -> pd.Series:
        tracks = self._read_dataframe(
            "select_top_tracks_for_date_range",
            {"min_stream_date": from_date, "max_stream_date": to_date},
        )
        return tracks["track_uri"]

    def insight_frames(
        self, filters: Mapping[str, Any]
    ) -> dict[str, pd.DataFrame]:
        with filtered_connection(filters) as (connection, params):
            query_params = self._wrapped_date_params(params)
            return {
                "distributions": self._read_dataframe_on(
                    connection,
                    "filtered_stream_distributions",
                    query_params,
                ),
                "total_streams": self._read_dataframe_on(
                    connection,
                    "filtered_total_streams_by_month",
                    query_params,
                ),
                "release_months": self._read_dataframe_on(
                    connection,
                    "filtered_release_month_counts",
                ),
                "discovery": self._read_dataframe_on(
                    connection,
                    "filtered_track_discovery_by_month",
                    query_params,
                ),
                "variety": self._read_dataframe_on(
                    connection,
                    "filtered_track_variety_by_month",
                    query_params,
                ),
                "weekday_by_month": self._read_dataframe_on(
                    connection,
                    "filtered_weekday_by_month_heatmap",
                    query_params,
                ),
                "month_by_year": self._read_dataframe_on(
                    connection,
                    "filtered_month_by_year_heatmap",
                    query_params,
                ),
                "hour_by_weekday": self._read_dataframe_on(
                    connection,
                    "filtered_hour_by_weekday_heatmap",
                    query_params,
                ),
            }

    def track_recommendations(
        self,
        filters: Mapping[str, Any],
        low_percentile: float,
        high_percentile: float,
        minimum_track_count: int,
    ) -> TrackRecommendations:
        params = parse_filters(dict(filters))
        has_filters = self._has_recommendation_filters(params)

        with filtered_connection(filters) as (connection, _):
            matching_track_count = None
            if has_filters:
                counts = self._read_dataframe_on(
                    connection,
                    "select_matching_track_count",
                )
                matching_track_count = int(counts.iloc[0]["cnt"])
                if matching_track_count < minimum_track_count:
                    return TrackRecommendations(
                        matching_track_count=matching_track_count,
                        tracks=None,
                    )

            tracks = self._read_dataframe_on(
                connection,
                "select_track_recommendations_percentile_range",
                {
                    "low_percentile": low_percentile,
                    "high_percentile": high_percentile,
                    "filter_tracks": has_filters,
                },
            )
        return TrackRecommendations(
            matching_track_count=matching_track_count,
            tracks=tracks,
        )

    def artist_stream_share_by_month(
        self, filters: Mapping[str, Any], n: int
    ) -> pd.DataFrame:
        return self._filtered_dataframe(
            filters,
            "filtered_artist_stream_share_by_month",
            lambda params: {"n": n, **self._wrapped_date_params(params)},
        )

    def genre_stream_share_by_month(
        self, filters: Mapping[str, Any], n: int
    ) -> pd.DataFrame:
        return self._filtered_dataframe(
            filters,
            "filtered_genre_stream_share_by_month",
            lambda params: {"n": n, **self._wrapped_date_params(params)},
        )

    def track_ranks_over_time(
        self, track_uris: Iterable[str], from_date, to_date
    ) -> pd.DataFrame:
        return self._read_dataframe(
            "track_ranks_over_time",
            {
                "track_uris": self._values_or_sentinel(track_uris, "EMPTY"),
                "from_date": from_date,
                "to_date": to_date,
            },
        )

    def artist_ranks_over_time(
        self, artist_uris: Iterable[str], from_date, to_date
    ) -> pd.DataFrame:
        return self._read_dataframe(
            "artist_ranks_over_time",
            {
                "artist_uris": self._values_or_sentinel(artist_uris, "EMPTY"),
                "from_date": from_date,
                "to_date": to_date,
            },
        )

    def album_ranks_over_time(
        self, album_uris: Iterable[str], from_date, to_date
    ) -> pd.DataFrame:
        return self._read_dataframe(
            "album_ranks_over_time",
            {
                "album_uris": self._values_or_sentinel(album_uris, "EMPTY"),
                "from_date": from_date,
                "to_date": to_date,
            },
        )

    def track_streams_by_month(
        self, track_uris: Iterable[str], from_date, to_date
    ) -> dict:
        rows = self._fetch_all(
            "select_track_streams_by_month",
            {
                "track_uris": self._values_or_sentinel(track_uris, "EMPTY"),
                "from_date": from_date,
                "to_date": to_date,
            },
        )
        return self._streams_by_month(
            rows,
            ["track_short_name", "track_name", "album_image_url"],
        )

    def artist_streams_by_month(
        self, artist_uris: Iterable[str], from_date, to_date
    ) -> dict:
        rows = self._fetch_all(
            "select_artist_streams_by_month",
            {
                "artist_uris": self._values_or_sentinel(artist_uris, "EMPTY"),
                "from_date": from_date,
                "to_date": to_date,
            },
        )
        return self._streams_by_month(
            rows,
            ["artist_name", "artist_image_url"],
        )

    def album_streams_by_month(
        self, album_uris: Iterable[str], from_date, to_date
    ) -> dict:
        rows = self._fetch_all(
            "select_album_streams_by_month",
            {
                "album_uris": self._values_or_sentinel(album_uris, "EMPTY"),
                "from_date": from_date,
                "to_date": to_date,
            },
        )
        return self._streams_by_month(
            rows,
            ["album_short_name", "album_name", "album_image_url"],
        )

    def filtered_track_ranks_over_time(
        self, filters: Mapping[str, Any], n: int
    ) -> pd.DataFrame:
        return self._filtered_rank_frame(
            filters,
            "filtered_track_ranks_over_time",
            n,
        )

    def filtered_artist_ranks_over_time(
        self, filters: Mapping[str, Any], n: int
    ) -> pd.DataFrame:
        return self._filtered_rank_frame(
            filters,
            "filtered_artist_ranks_over_time",
            n,
        )

    def filtered_album_ranks_over_time(
        self, filters: Mapping[str, Any], n: int
    ) -> pd.DataFrame:
        return self._filtered_rank_frame(
            filters,
            "filtered_album_ranks_over_time",
            n,
        )

    def filtered_track_streams_by_month(
        self, filters: Mapping[str, Any], n: int
    ) -> dict:
        return self._filtered_streams_by_month(
            filters,
            "filtered_track_streams_by_month",
            n,
            ["track_short_name", "track_name", "album_image_url"],
        )

    def filtered_artist_streams_by_month(
        self, filters: Mapping[str, Any], n: int
    ) -> dict:
        return self._filtered_streams_by_month(
            filters,
            "filtered_artist_streams_by_month",
            n,
            ["artist_name", "artist_image_url"],
        )

    def filtered_album_streams_by_month(
        self, filters: Mapping[str, Any], n: int
    ) -> dict:
        return self._filtered_streams_by_month(
            filters,
            "filtered_album_streams_by_month",
            n,
            ["album_short_name", "album_name", "album_image_url"],
        )

    def orphan_tracks(self) -> list[tuple]:
        return self._fetch_all("select_orphan_tracks")

    def matching_track_for_orphan(self, track_uri: str) -> tuple | None:
        return self._fetch_one(
            "select_matching_track",
            {"orphan_uri": track_uri},
        )

    def repair_orphan_track(self, orphan_uri: str, replacement_uri: str) -> None:
        self._execute_write(
            "repair_orphan_track",
            {"orphan_uri": orphan_uri, "replacement_uri": replacement_uri},
        )

    def delete_orphan_albums(self) -> None:
        self._execute_write("delete_orphan_albums")

    def delete_orphan_artists(self) -> None:
        self._execute_write("delete_orphan_artists")

    def track_uris_without_metadata(self) -> list[str]:
        return [
            row[0]
            for row in self._fetch_all("select_streams_without_tracks")
        ]

    @contextmanager
    def stream_writer(self) -> Iterator[StreamWriter]:
        with get_connection() as connection:
            writer = StreamWriter(connection.cursor())
            yield writer
            connection.commit()

    def save_streams(self, streams: Iterable[Mapping[str, Any]]) -> None:
        with self.stream_writer() as writer:
            for stream in streams:
                writer.add(stream["track_uri"], stream["played_at"])

    def album_labels(self) -> pd.DataFrame:
        return self._read_dataframe("select_album_labels")

    def replace_standardized_labels(
        self, labels: Iterable[Mapping[str, str]]
    ) -> None:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query_text("truncate_record_labels"))
            cursor.executemany(query_text("insert_record_label"), labels)
            connection.commit()

    def orphan_stream_uris(self) -> list[str]:
        return [
            row[0]
            for row in self._fetch_all("select_orphan_stream_uris")
        ]

    def track_stream_count(self, track_uri: str) -> int:
        row = self._fetch_one(
            "select_track_stream_count",
            {"track_uri": track_uri},
        )
        return int(row[0])

    def matching_track_by_name_artist(
        self, track_name: str, artist_name: str
    ) -> tuple | None:
        return self._fetch_one(
            "select_matching_track_by_name_artist",
            {"track_name": track_name, "artist_name": artist_name},
        )

    def delete_streams_for_track(
        self, track_uri: str, commit: bool = False
    ) -> None:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                query_text("delete_streams_for_track"),
                {"track_uri": track_uri},
            )
            if commit:
                connection.commit()
            else:
                connection.rollback()

    def queue_job(self, job_type: str, arguments: str, status: str) -> None:
        self._execute_write(
            "insert_job",
            {
                "job_type": job_type,
                "arguments": arguments,
                "status": status,
            },
        )

    def next_queued_job(self, status: str) -> QueuedJob | None:
        row = self._fetch_one("select_next_queued_job", {"status": status})
        if row is None:
            return None
        return QueuedJob(id=row[0], type=row[1], arguments=row[2])

    def mark_job_started(self, job_id: int, status: str) -> None:
        self._execute_write(
            "update_job_started",
            {"id": job_id, "status": status},
        )

    def mark_job_succeeded(self, job_id: int, status: str) -> None:
        self._execute_write(
            "update_job_succeeded",
            {"id": job_id, "status": status},
        )

    def mark_job_failed(self, job_id: int, status: str, error: str) -> None:
        self._execute_write(
            "update_job_failed",
            {"id": job_id, "status": status, "error": error},
        )

    def expire_stale_jobs(
        self, failure_status: str, in_progress_status: str
    ) -> int:
        return self._execute_write(
            "expire_stale_jobs",
            {
                "failure_status": failure_status,
                "in_progress_status": in_progress_status,
            },
        )

    def _read_dataframe(
        self, query_name: str, params: Mapping[str, Any] | None = None
    ) -> pd.DataFrame:
        with get_engine().begin() as connection:
            return self._read_dataframe_on(connection, query_name, params)

    @staticmethod
    def _read_dataframe_on(
        connection,
        query_name: str,
        params: Mapping[str, Any] | None = None,
    ) -> pd.DataFrame:
        return pd.read_sql_query(
            sqlalchemy.text(query_text(query_name)),
            connection,
            params=params,
        )

    def _filtered_dataframe(
        self,
        filters: Mapping[str, Any],
        query_name: str,
        params_factory: Callable[
            [Mapping[str, Any]], Mapping[str, Any] | None
        ]
        | None = None,
    ) -> pd.DataFrame:
        with filtered_connection(filters) as (connection, filter_params):
            params = (
                params_factory(filter_params)
                if params_factory is not None
                else None
            )
            return self._read_dataframe_on(
                connection,
                query_name,
                params,
            )

    def _filtered_rank_frame(
        self, filters: Mapping[str, Any], query_name: str, n: int
    ) -> pd.DataFrame:
        return self._filtered_dataframe(
            filters,
            query_name,
            lambda params: {
                "from_date": params["wrapped_start_date"],
                "to_date": params["wrapped_end_date"],
                "n": n,
            },
        )

    def _filtered_streams_by_month(
        self,
        filters: Mapping[str, Any],
        query_name: str,
        n: int,
        metadata_columns: list[str],
    ) -> dict:
        frame = self._filtered_rank_frame(filters, query_name, n)
        return self._streams_by_month(
            frame.itertuples(index=False, name=None),
            metadata_columns,
        )

    @staticmethod
    def _wrapped_date_params(params: Mapping[str, Any]) -> dict:
        return {
            "wrapped_start_date": params["wrapped_start_date"],
            "wrapped_end_date": params["wrapped_end_date"],
        }

    @staticmethod
    def _values_or_sentinel(
        values: Iterable[Any], empty_sentinel: Any
    ) -> tuple:
        result = tuple(values)
        return result if result else (empty_sentinel,)

    @staticmethod
    def _has_recommendation_filters(params: Mapping[str, Any]) -> bool:
        return any(
            [
                params["filter_tracks"],
                params["filter_playlists"],
                params["filter_artists"],
                params["filter_albums"],
                params["filter_labels"],
                params["filter_genres"],
                params["filter_producers"],
                params["filter_years"],
                params["liked"],
                params["wrapped_start_date"] is not None,
            ]
        )

    @staticmethod
    def _streams_by_month(
        rows: Iterable[tuple], metadata_fields: list[str]
    ) -> dict:
        streams = {}
        metadata = {}
        for row in rows:
            uri = row[0]
            year = int(row[1])
            month = int(row[2])
            stream_count = int(row[3])
            streams.setdefault(uri, {}).setdefault(year, {})[month] = stream_count
            if uri not in metadata:
                metadata[uri] = {
                    field: row[4 + index]
                    for index, field in enumerate(metadata_fields)
                }
        return {"streams": streams, "metadata": metadata}

    def _fetch_all(
        self, query_name: str, params: Mapping[str, Any] | None = None
    ) -> list[tuple]:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query_text(query_name), params)
            return cursor.fetchall()

    def _fetch_one(
        self, query_name: str, params: Mapping[str, Any] | None = None
    ) -> tuple | None:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query_text(query_name), params)
            return cursor.fetchone()

    def _execute_write(
        self, query_name: str, params: Mapping[str, Any] | None = None
    ) -> int:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query_text(query_name), params)
            affected_rows = cursor.rowcount
            connection.commit()
        return affected_rows
