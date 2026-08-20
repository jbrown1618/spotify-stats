from datetime import datetime, timedelta
from typing import Any, Iterable


class MusicBrainzStore:
    def __init__(self, cursor, retry_days: int):
        self.cursor = cursor
        self.retry_days = retry_days

    def fetch_unfetched_tracks(self, limit: int) -> list[dict[str, Any]]:
        self.cursor.execute(
            """
            SELECT
                t.uri,
                t.name,
                t.isrc,
                COALESCE(stream_counts.stream_count, 0),
                ARRAY_AGG(a.uri ORDER BY ta.artist_index),
                ARRAY_AGG(a.name ORDER BY ta.artist_index)
            FROM track t
                INNER JOIN track_artist ta ON ta.track_uri = t.uri
                INNER JOIN artist a ON a.uri = ta.artist_uri
                LEFT JOIN liked_track lt ON lt.track_uri = t.uri
                LEFT JOIN (
                    SELECT track_uri, COUNT(*) AS stream_count
                    FROM track_stream
                    GROUP BY track_uri
                ) stream_counts ON stream_counts.track_uri = t.uri
            WHERE t.isrc IS NOT NULL
                AND (
                    lt.track_uri IS NOT NULL
                    OR EXISTS (
                        SELECT 1 FROM playlist_track pt WHERE pt.track_uri = t.uri
                    )
                )
                AND (
                    NOT EXISTS (
                        SELECT 1
                        FROM sp_track_mb_recording stmr
                        WHERE stmr.spotify_track_uri = t.uri
                    )
                    OR EXISTS (
                        SELECT 1
                        FROM sp_track_mb_recording stmr
                        WHERE stmr.spotify_track_uri = t.uri
                            AND NOT EXISTS (
                                SELECT 1
                                FROM mb_recording_credit mrc
                                WHERE mrc.recording_mbid = stmr.recording_mbid
                            )
                    )
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM mb_unfetchable_isrc mui
                    WHERE mui.isrc = t.isrc
                        AND mui.retry_after > CURRENT_TIMESTAMP
                )
            GROUP BY t.uri, t.name, t.isrc, stream_counts.stream_count, lt.track_uri
            ORDER BY
                COALESCE(stream_counts.stream_count, 0) DESC,
                (lt.track_uri IS NOT NULL) DESC,
                t.name
            LIMIT %(limit)s;
            """,
            {"limit": limit},
        )
        return [
            {
                "track_uri": row[0],
                "track_name": row[1],
                "isrc": row[2],
                "stream_count": row[3],
                "artist_uris": row[4],
                "artist_names": row[5],
            }
            for row in self.cursor.fetchall()
        ]

    def fetch_unmatched_liked_artists(self) -> list[dict[str, str]]:
        self.cursor.execute(
            """
            SELECT DISTINCT a.uri, a.name
            FROM liked_track lt
                INNER JOIN track_artist ta ON ta.track_uri = lt.track_uri
                INNER JOIN artist a ON a.uri = ta.artist_uri
            WHERE NOT EXISTS (
                SELECT 1
                FROM sp_artist_mb_artist sama
                WHERE sama.spotify_artist_uri = a.uri
            )
            AND NOT EXISTS (
                SELECT 1
                FROM mb_unmatchable_artist mua
                WHERE mua.artist_uri = a.uri
                    AND mua.retry_after > CURRENT_TIMESTAMP
            )
            ORDER BY a.name;
            """
        )
        return [
            {"artist_uri": row[0], "artist_name": row[1]}
            for row in self.cursor.fetchall()
        ]

    def save_recording(self, recording: dict[str, Any], language: str | None):
        self.cursor.execute(
            """
            INSERT INTO mb_recording (recording_mbid, recording_title, recording_language)
            VALUES (%(recording_mbid)s, %(recording_title)s, %(recording_language)s)
            ON CONFLICT (recording_mbid) DO UPDATE SET
                recording_title = EXCLUDED.recording_title,
                recording_language = EXCLUDED.recording_language;
            """,
            {
                "recording_mbid": recording["id"],
                "recording_title": recording["title"],
                "recording_language": language,
            },
        )

    def replace_recording_credits(
        self,
        recording_mbid: str,
        credits: Iterable[dict[str, Any]],
    ):
        self.cursor.execute(
            "DELETE FROM mb_recording_credit WHERE recording_mbid = %(recording_mbid)s;",
            {"recording_mbid": recording_mbid},
        )
        for credit in credits:
            self.cursor.execute(
                """
                INSERT INTO mb_recording_credit (
                    recording_mbid,
                    artist_mbid,
                    raw_role,
                    credit_type,
                    credit_details
                ) VALUES (
                    %(recording_mbid)s,
                    %(artist_mbid)s,
                    %(raw_role)s,
                    %(credit_type)s,
                    %(credit_details)s
                )
                ON CONFLICT DO NOTHING;
                """,
                {"recording_mbid": recording_mbid, **credit},
            )

    def save_track_mapping(self, spotify_track_uri: str, recording_mbid: str):
        self.cursor.execute(
            """
            INSERT INTO sp_track_mb_recording (spotify_track_uri, recording_mbid)
            VALUES (%(spotify_track_uri)s, %(recording_mbid)s)
            ON CONFLICT DO NOTHING;
            """,
            {
                "spotify_track_uri": spotify_track_uri,
                "recording_mbid": recording_mbid,
            },
        )

    def has_artist(self, artist_mbid: str) -> bool:
        self.cursor.execute(
            """
            SELECT 1
            FROM mb_artist
            WHERE artist_mbid = %(artist_mbid)s;
            """,
            {"artist_mbid": artist_mbid},
        )
        return self.cursor.fetchone() is not None

    def save_artist(self, artist: dict[str, Any]):
        self.cursor.execute(
            """
            INSERT INTO mb_artist (
                artist_mbid,
                artist_mb_name,
                artist_sort_name,
                artist_disambiguation,
                artist_type,
                artist_area,
                artist_birthplace,
                artist_start_date,
                artist_end_date,
                artist_gender
            ) VALUES (
                %(artist_mbid)s,
                %(artist_mb_name)s,
                %(artist_sort_name)s,
                %(artist_disambiguation)s,
                %(artist_type)s,
                %(artist_area)s,
                %(artist_birthplace)s,
                %(artist_start_date)s,
                %(artist_end_date)s,
                %(artist_gender)s
            )
            ON CONFLICT (artist_mbid) DO UPDATE SET
                artist_mb_name = EXCLUDED.artist_mb_name,
                artist_sort_name = EXCLUDED.artist_sort_name,
                artist_disambiguation = EXCLUDED.artist_disambiguation,
                artist_type = EXCLUDED.artist_type,
                artist_area = EXCLUDED.artist_area,
                artist_birthplace = EXCLUDED.artist_birthplace,
                artist_start_date = EXCLUDED.artist_start_date,
                artist_end_date = EXCLUDED.artist_end_date,
                artist_gender = EXCLUDED.artist_gender;
            """,
            artist,
        )

    def replace_artist_aliases(self, artist_mbid: str, aliases: Iterable[dict[str, Any]]):
        self.cursor.execute(
            "DELETE FROM mb_artist_alias WHERE artist_mbid = %(artist_mbid)s;",
            {"artist_mbid": artist_mbid},
        )
        for alias in aliases:
            self.cursor.execute(
                """
                INSERT INTO mb_artist_alias (
                    artist_mbid,
                    alias_name,
                    sort_name,
                    locale,
                    alias_type,
                    primary_for_locale
                ) VALUES (
                    %(artist_mbid)s,
                    %(alias_name)s,
                    %(sort_name)s,
                    %(locale)s,
                    %(alias_type)s,
                    %(primary_for_locale)s
                )
                ON CONFLICT DO NOTHING;
                """,
                {"artist_mbid": artist_mbid, **alias},
            )

    def save_artist_relationships(
        self,
        relationships: Iterable[dict[str, str]],
    ):
        for relationship in relationships:
            self.cursor.execute(
                """
                INSERT INTO mb_artist_relationship (
                    artist_mbid,
                    other_mbid,
                    relationship_type
                ) VALUES (
                    %(artist_mbid)s,
                    %(other_mbid)s,
                    %(relationship_type)s
                )
                ON CONFLICT DO NOTHING;
                """,
                relationship,
            )

    def matching_spotify_artists(self, names: Iterable[str]) -> list[str]:
        normalized_names = sorted({name.strip().casefold() for name in names if name})
        if not normalized_names:
            return []
        self.cursor.execute(
            """
            SELECT uri
            FROM artist
            WHERE LOWER(BTRIM(name)) = ANY(%(names)s)
            ORDER BY uri;
            """,
            {"names": normalized_names},
        )
        return [row[0] for row in self.cursor.fetchall()]

    def save_artist_mapping(self, spotify_artist_uri: str, artist_mbid: str):
        self.cursor.execute(
            """
            INSERT INTO sp_artist_mb_artist (spotify_artist_uri, artist_mbid)
            VALUES (%(spotify_artist_uri)s, %(artist_mbid)s)
            ON CONFLICT DO NOTHING;
            """,
            {
                "spotify_artist_uri": spotify_artist_uri,
                "artist_mbid": artist_mbid,
            },
        )

    def mark_unfetchable_isrc(self, isrc: str, reason: str):
        self.cursor.execute(
            """
            INSERT INTO mb_unfetchable_isrc (isrc, reason, retry_after, updated_at)
            VALUES (%(isrc)s, %(reason)s, %(retry_after)s, CURRENT_TIMESTAMP)
            ON CONFLICT (isrc) DO UPDATE SET
                reason = EXCLUDED.reason,
                retry_after = EXCLUDED.retry_after,
                updated_at = CURRENT_TIMESTAMP;
            """,
            {
                "isrc": isrc,
                "reason": reason,
                "retry_after": datetime.now() + timedelta(days=self.retry_days),
            },
        )

    def mark_unmatchable_artist(self, artist_uri: str, artist_name: str, reason: str):
        self.cursor.execute(
            """
            INSERT INTO mb_unmatchable_artist (
                artist_uri,
                artist_name,
                reason,
                retry_after,
                updated_at
            ) VALUES (
                %(artist_uri)s,
                %(artist_name)s,
                %(reason)s,
                %(retry_after)s,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT (artist_uri) DO UPDATE SET
                artist_name = EXCLUDED.artist_name,
                reason = EXCLUDED.reason,
                retry_after = EXCLUDED.retry_after,
                updated_at = CURRENT_TIMESTAMP;
            """,
            {
                "artist_uri": artist_uri,
                "artist_name": artist_name,
                "reason": reason,
                "retry_after": datetime.now() + timedelta(days=self.retry_days),
            },
        )