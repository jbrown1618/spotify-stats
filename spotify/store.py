from typing import Any, Iterable

from psycopg2.extras import execute_values


class SpotifyStore:
    def __init__(self, cursor):
        self.cursor = cursor

    def save_playlists(self, playlists: Iterable[dict[str, Any]]):
        self._upsert(
            "playlist",
            (
                "uri",
                "name",
                "collaborative",
                "public",
                "image_url",
                "owner",
            ),
            ("uri",),
            playlists,
        )

    def save_tracks(self, tracks: Iterable[dict[str, Any]]):
        self._upsert(
            "track",
            (
                "uri",
                "name",
                "short_name",
                "popularity",
                "explicit",
                "duration_ms",
                "album_uri",
                "isrc",
            ),
            ("uri",),
            tracks,
        )

    def save_albums(self, albums: Iterable[dict[str, Any]]):
        self._upsert(
            "album",
            (
                "uri",
                "name",
                "short_name",
                "album_type",
                "label",
                "popularity",
                "total_tracks",
                "release_date",
                "image_url",
            ),
            ("uri",),
            albums,
        )

    def save_artists(self, artists: Iterable[dict[str, Any]]):
        self._upsert(
            "artist",
            ("uri", "name", "popularity", "followers", "image_url"),
            ("uri",),
            artists,
        )

    def save_track_artists(self, track_artists: Iterable[dict[str, Any]]):
        self._upsert(
            "track_artist",
            ("track_uri", "artist_uri", "artist_index"),
            ("track_uri", "artist_uri"),
            track_artists,
        )

    def save_album_artists(self, album_artists: Iterable[dict[str, Any]]):
        self._upsert(
            "album_artist",
            ("album_uri", "artist_uri"),
            ("album_uri", "artist_uri"),
            album_artists,
        )

    def save_artist_genres(self, artist_genres: Iterable[dict[str, Any]]):
        self._upsert(
            "artist_genre",
            ("artist_uri", "genre"),
            ("artist_uri", "genre"),
            artist_genres,
        )

    def replace_liked_tracks(self, liked_tracks: Iterable[dict[str, Any]]):
        self.cursor.execute("TRUNCATE liked_track;")
        self._upsert(
            "liked_track",
            ("track_uri",),
            ("track_uri",),
            liked_tracks,
        )

    def replace_playlist_tracks(
        self,
        playlist_tracks: Iterable[dict[str, Any]],
    ):
        self.cursor.execute("TRUNCATE playlist_track;")
        self._upsert(
            "playlist_track",
            ("playlist_uri", "track_uri"),
            ("playlist_uri", "track_uri"),
            playlist_tracks,
        )

    def _upsert(
        self,
        table: str,
        columns: tuple[str, ...],
        conflict_columns: tuple[str, ...],
        rows: Iterable[dict[str, Any]],
    ):
        values = [tuple(row.get(column) for column in columns) for row in rows]
        if not values:
            return

        update_columns = [
            column for column in columns if column not in conflict_columns
        ]
        if update_columns:
            conflict_action = "DO UPDATE SET " + ", ".join(
                f"{column} = EXCLUDED.{column}" for column in update_columns
            )
        else:
            conflict_action = "DO NOTHING"

        statement = f"""
            INSERT INTO {table} ({", ".join(columns)})
            VALUES %s
            ON CONFLICT ({", ".join(conflict_columns)}) {conflict_action};
        """
        execute_values(self.cursor, statement, values, page_size=500)
