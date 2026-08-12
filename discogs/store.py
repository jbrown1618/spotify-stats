from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from psycopg2.extras import Json


role_details = re.compile(r"\[(.+)\]")


@dataclass
class SpotifyTrack:
    track_uri: str
    track_name: str
    duration_ms: int | None
    album_uri: str
    album_name: str
    album_release_date: str | None
    stream_count: int
    artist_uris: list[str]
    artist_names: list[str]


def fetch_unfetched_tracks(cursor, limit: int) -> list[SpotifyTrack]:
    cursor.execute(
        """
        SELECT
            t.uri AS track_uri,
            t.name AS track_name,
            t.duration_ms,
            t.album_uri,
            al.name AS album_name,
            al.release_date AS album_release_date,
            COALESCE(stream_counts.stream_count, 0) AS stream_count,
            ARRAY_AGG(a.uri ORDER BY ta.artist_index) AS artist_uris,
            ARRAY_AGG(a.name ORDER BY ta.artist_index) AS artist_names
        FROM track t
            INNER JOIN album al ON t.album_uri = al.uri
            INNER JOIN track_artist ta ON t.uri = ta.track_uri
            INNER JOIN artist a ON ta.artist_uri = a.uri
            LEFT JOIN liked_track lt ON t.uri = lt.track_uri
            LEFT JOIN (
                SELECT track_uri, COUNT(*) AS stream_count
                FROM track_stream
                GROUP BY track_uri
            ) stream_counts ON t.uri = stream_counts.track_uri
        WHERE NOT EXISTS (
            SELECT 1
            FROM sp_track_discogs_track stdt
            WHERE stdt.spotify_track_uri = t.uri
        )
        AND NOT EXISTS (
            SELECT 1
            FROM discogs_unmatchable_track dut
            WHERE dut.spotify_track_uri = t.uri
        )
        GROUP BY
            t.uri,
            t.name,
            t.duration_ms,
            t.album_uri,
            al.name,
            al.release_date,
            stream_counts.stream_count,
            lt.track_uri
        ORDER BY
            COALESCE(stream_counts.stream_count, 0) DESC,
            (lt.track_uri IS NOT NULL) DESC,
            al.release_date DESC NULLS LAST,
            t.name
        LIMIT %(limit)s;
        """,
        {"limit": limit},
    )
    return [
        SpotifyTrack(
            track_uri=row[0],
            track_name=row[1],
            duration_ms=row[2],
            album_uri=row[3],
            album_name=row[4],
            album_release_date=row[5],
            stream_count=row[6],
            artist_uris=row[7],
            artist_names=row[8],
        )
        for row in cursor.fetchall()
    ]


def matched_discogs_artist_id(cursor, spotify_artist_uri: str) -> int | None:
    cursor.execute(
        """
        SELECT discogs_artist_id
        FROM sp_artist_discogs_artist
        WHERE spotify_artist_uri = %(spotify_artist_uri)s
        ORDER BY confidence DESC NULLS LAST
        LIMIT 1;
        """,
        {"spotify_artist_uri": spotify_artist_uri},
    )
    existing = cursor.fetchone()
    if existing is None:
        return None

    return existing[0]


def is_unmatchable_artist(cursor, spotify_artist_uri: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM discogs_unmatchable_artist
        WHERE spotify_artist_uri = %(spotify_artist_uri)s;
        """,
        {"spotify_artist_uri": spotify_artist_uri},
    )
    return cursor.fetchone() is not None


def unique_spotify_artist_uri_for_discogs_name(
    cursor,
    artist_name: str,
    discogs_artist_id: int,
) -> str | None:
    cursor.execute(
        """
        SELECT a.uri
        FROM artist a
        WHERE lower(a.name) = lower(%(artist_name)s)
            AND NOT EXISTS (
                SELECT 1
                FROM sp_artist_discogs_artist sada
                WHERE sada.spotify_artist_uri = a.uri
                    AND sada.discogs_artist_id != %(discogs_artist_id)s
            )
        LIMIT 2;
        """,
        {
            "artist_name": artist_name,
            "discogs_artist_id": discogs_artist_id,
        },
    )
    matches = cursor.fetchall()
    if len(matches) != 1:
        return None
    return matches[0][0]


def save_artist(cursor, artist: dict[str, Any]):
    artist_id = int(artist["id"])
    cursor.execute(
        """
        INSERT INTO discogs_artist
            (
                discogs_artist_id,
                name,
                realname,
                profile,
                primary_image_url,
                namevariations,
                updated_at
            )
        VALUES
            (
                %(discogs_artist_id)s,
                %(name)s,
                %(realname)s,
                %(profile)s,
                %(primary_image_url)s,
                %(namevariations)s,
                CURRENT_TIMESTAMP
            )
        ON CONFLICT (discogs_artist_id) DO UPDATE
        SET
            name = EXCLUDED.name,
            realname = EXCLUDED.realname,
            profile = EXCLUDED.profile,
            primary_image_url = EXCLUDED.primary_image_url,
            namevariations = EXCLUDED.namevariations,
            updated_at = CURRENT_TIMESTAMP;
        """,
        {
            "discogs_artist_id": artist_id,
            "name": artist["name"],
            "realname": artist.get("realname"),
            "profile": artist.get("profile"),
            "primary_image_url": primary_image_url(artist.get("images", [])),
            "namevariations": json_param(artist.get("namevariations")),
        },
    )


def save_artist_mapping(
    cursor,
    spotify_artist_uri: str,
    discogs_artist_id: int,
    confidence: int,
    match_method: str,
):
    cursor.execute(
        """
        INSERT INTO sp_artist_discogs_artist
            (spotify_artist_uri, discogs_artist_id, confidence, match_method)
        VALUES
            (%(spotify_artist_uri)s, %(discogs_artist_id)s, %(confidence)s, %(match_method)s)
        ON CONFLICT (spotify_artist_uri, discogs_artist_id) DO UPDATE
        SET
            confidence = EXCLUDED.confidence,
            match_method = EXCLUDED.match_method;
        """,
        {
            "spotify_artist_uri": spotify_artist_uri,
            "discogs_artist_id": discogs_artist_id,
            "confidence": confidence,
            "match_method": match_method,
        },
    )


def save_master(cursor, master: dict[str, Any]):
    master_id = int(master["id"] if "id" in master else master["discogs_master_id"])
    cursor.execute(
        """
        INSERT INTO discogs_master
            (discogs_master_id, title, year, updated_at)
        VALUES
            (
                %(discogs_master_id)s,
                %(title)s,
                %(year)s,
                CURRENT_TIMESTAMP
            )
        ON CONFLICT (discogs_master_id) DO UPDATE
        SET
            title = EXCLUDED.title,
            year = EXCLUDED.year,
            updated_at = CURRENT_TIMESTAMP;
        """,
        {
            "discogs_master_id": master_id,
            "title": master["title"],
            "year": parse_int(master.get("year")),
        },
    )

    save_master_genres(cursor, master_id, master.get("genres", []), "genre")
    save_master_genres(cursor, master_id, master.get("styles", []), "style")
    save_tracks_and_credits(cursor, "master", master_id, master_id, master.get("tracklist", []))
    save_entity_credits(cursor, "master", master_id, master_id, master.get("extraartists", []))
    save_videos(cursor, master_id, master.get("videos", []))


def save_master_genres(cursor, master_id: int, genres: list[str], genre_source: str):
    cursor.execute(
        """
        DELETE FROM discogs_master_genre
        WHERE discogs_master_id = %(discogs_master_id)s
            AND genre_source = %(genre_source)s;
        """,
        {
            "discogs_master_id": master_id,
            "genre_source": genre_source,
        },
    )

    for genre in genres or []:
        cursor.execute(
            """
            INSERT INTO discogs_master_genre
                (discogs_master_id, genre, genre_source)
            VALUES
                (%(discogs_master_id)s, %(genre)s, %(genre_source)s)
            ON CONFLICT DO NOTHING;
            """,
            {
                "discogs_master_id": master_id,
                "genre": genre,
                "genre_source": genre_source,
            },
        )


def save_release(cursor, release: dict[str, Any], master_id: int):
    release_id = int(release["id"])
    cursor.execute(
        """
        INSERT INTO discogs_release
            (
                discogs_release_id,
                discogs_master_id,
                title,
                year,
                country,
                released,
                labels,
                companies,
                formats,
                identifiers,
                updated_at
            )
        VALUES
            (
                %(discogs_release_id)s,
                %(discogs_master_id)s,
                %(title)s,
                %(year)s,
                %(country)s,
                %(released)s,
                %(labels)s,
                %(companies)s,
                %(formats)s,
                %(identifiers)s,
                CURRENT_TIMESTAMP
            )
        ON CONFLICT (discogs_release_id) DO UPDATE
        SET
            discogs_master_id = EXCLUDED.discogs_master_id,
            title = EXCLUDED.title,
            year = EXCLUDED.year,
            country = EXCLUDED.country,
            released = EXCLUDED.released,
            labels = EXCLUDED.labels,
            companies = EXCLUDED.companies,
            formats = EXCLUDED.formats,
            identifiers = EXCLUDED.identifiers,
            updated_at = CURRENT_TIMESTAMP;
        """,
        {
            "discogs_release_id": release_id,
            "discogs_master_id": parse_int(release.get("master_id")) or master_id,
            "title": release["title"],
            "year": parse_int(release.get("year")),
            "country": release.get("country"),
            "released": release.get("released"),
            "labels": json_param_without_urls(release.get("labels")),
            "companies": json_param_without_urls(release.get("companies")),
            "formats": json_param_without_urls(release.get("formats")),
            "identifiers": json_param_without_urls(release.get("identifiers")),
        },
    )

    save_tracks_and_credits(cursor, "release", release_id, master_id, release.get("tracklist", []))
    save_entity_credits(cursor, "release", release_id, master_id, release.get("extraartists", []))


def save_track_mapping(
    cursor,
    spotify_track_uri: str,
    discogs_master_id: int,
    discogs_track_position: str,
    discogs_track_title: str,
    confidence: int,
    match_method: str,
):
    cursor.execute(
        """
        INSERT INTO sp_track_discogs_track
            (
                spotify_track_uri,
                discogs_master_id,
                discogs_track_position,
                discogs_track_title,
                confidence,
                match_method
            )
        VALUES
            (
                %(spotify_track_uri)s,
                %(discogs_master_id)s,
                %(discogs_track_position)s,
                %(discogs_track_title)s,
                %(confidence)s,
                %(match_method)s
            )
        ON CONFLICT (spotify_track_uri, discogs_master_id, discogs_track_position, discogs_track_title) DO UPDATE
        SET
            confidence = EXCLUDED.confidence,
            match_method = EXCLUDED.match_method;
        """,
        {
            "spotify_track_uri": spotify_track_uri,
            "discogs_master_id": discogs_master_id,
            "discogs_track_position": discogs_track_position,
            "discogs_track_title": discogs_track_title,
            "confidence": confidence,
            "match_method": match_method,
        },
    )


def save_album_mapping(
    cursor,
    spotify_album_uri: str,
    discogs_master_id: int,
    confidence: int,
    match_method: str,
):
    cursor.execute(
        """
        INSERT INTO sp_album_discogs_master
            (spotify_album_uri, discogs_master_id, confidence, match_method)
        VALUES
            (%(spotify_album_uri)s, %(discogs_master_id)s, %(confidence)s, %(match_method)s)
        ON CONFLICT (spotify_album_uri, discogs_master_id) DO UPDATE
        SET
            confidence = EXCLUDED.confidence,
            match_method = EXCLUDED.match_method;
        """,
        {
            "spotify_album_uri": spotify_album_uri,
            "discogs_master_id": discogs_master_id,
            "confidence": confidence,
            "match_method": match_method,
        },
    )


def mark_unmatchable_artist(cursor, spotify_artist_uri: str, artist_name: str, reason: str):
    cursor.execute(
        """
        INSERT INTO discogs_unmatchable_artist
            (spotify_artist_uri, artist_name, reason, updated_at)
        VALUES
            (%(spotify_artist_uri)s, %(artist_name)s, %(reason)s, CURRENT_TIMESTAMP)
        ON CONFLICT (spotify_artist_uri) DO UPDATE
        SET
            artist_name = EXCLUDED.artist_name,
            reason = EXCLUDED.reason,
            updated_at = CURRENT_TIMESTAMP;
        """,
        {
            "spotify_artist_uri": spotify_artist_uri,
            "artist_name": artist_name,
            "reason": reason,
        },
    )


def mark_unmatchable_track(cursor, spotify_track_uri: str, track_name: str, reason: str):
    cursor.execute(
        """
        INSERT INTO discogs_unmatchable_track
            (spotify_track_uri, track_name, reason, updated_at)
        VALUES
            (%(spotify_track_uri)s, %(track_name)s, %(reason)s, CURRENT_TIMESTAMP)
        ON CONFLICT (spotify_track_uri) DO UPDATE
        SET
            track_name = EXCLUDED.track_name,
            reason = EXCLUDED.reason,
            updated_at = CURRENT_TIMESTAMP;
        """,
        {
            "spotify_track_uri": spotify_track_uri,
            "track_name": track_name,
            "reason": reason,
        },
    )


def delete_artist_memberships(cursor, group_artist_id: int):
    cursor.execute(
        """
        DELETE FROM discogs_artist_membership
        WHERE group_discogs_artist_id = %(group_discogs_artist_id)s;
        """,
        {"group_discogs_artist_id": group_artist_id},
    )


def save_artist_membership(cursor, group_artist_id: int, member_artist_id: int, active: bool | None):
    cursor.execute(
        """
        INSERT INTO discogs_artist_membership
            (group_discogs_artist_id, member_discogs_artist_id, active)
        VALUES
            (%(group_discogs_artist_id)s, %(member_discogs_artist_id)s, %(active)s)
        ON CONFLICT (group_discogs_artist_id, member_discogs_artist_id) DO UPDATE
        SET
            active = EXCLUDED.active;
        """,
        {
            "group_discogs_artist_id": group_artist_id,
            "member_discogs_artist_id": member_artist_id,
            "active": active,
        },
    )


def save_minimal_artist(cursor, artist: dict[str, Any]):
    artist_id = parse_int(artist.get("id"))
    name = artist.get("name")
    if artist_id is None or artist_id <= 0 or not name:
        return

    cursor.execute(
        """
        INSERT INTO discogs_artist
            (discogs_artist_id, name, updated_at)
        VALUES
            (%(discogs_artist_id)s, %(name)s, CURRENT_TIMESTAMP)
        ON CONFLICT (discogs_artist_id) DO UPDATE
        SET
            name = COALESCE(discogs_artist.name, EXCLUDED.name),
            updated_at = CURRENT_TIMESTAMP;
        """,
        {
            "discogs_artist_id": artist_id,
            "name": name,
        },
    )


def save_tracks_and_credits(
    cursor,
    source_type: str,
    source_id: int,
    master_id: int,
    tracklist: list[dict[str, Any]],
):
    for track in tracklist or []:
        if track.get("type_") != "track":
            continue

        position = track.get("position") or ""
        title = track.get("title")
        if not title:
            continue

        if source_type == "master":
            cursor.execute(
                """
                INSERT INTO discogs_track
                    (discogs_master_id, position, title)
                VALUES
                    (%(discogs_master_id)s, %(position)s, %(title)s)
                ON CONFLICT (discogs_master_id, position, title) DO UPDATE
                SET
                    title = EXCLUDED.title;
                """,
                {
                    "discogs_master_id": master_id,
                    "position": position,
                    "title": title,
                },
            )

        save_credits(
            cursor,
            source_type,
            source_id,
            master_id,
            "track",
            position,
            title,
            track.get("extraartists", []),
        )


def save_entity_credits(
    cursor,
    source_type: str,
    source_id: int,
    master_id: int,
    extraartists: list[dict[str, Any]],
):
    save_credits(cursor, source_type, source_id, master_id, "entity", None, None, extraartists)


def save_credits(
    cursor,
    source_type: str,
    source_id: int,
    master_id: int,
    scope: str,
    track_position: str | None,
    track_title: str | None,
    extraartists: list[dict[str, Any]],
):
    for artist in extraartists or []:
        artist_name = artist.get("name")
        if not artist_name:
            continue

        save_minimal_artist(cursor, artist)
        artist_id = parse_int(artist.get("id"))

        for raw_role in split_roles(artist.get("role")):
            credit_type, credit_details = standardize_credit_role(raw_role)
            cursor.execute(
                """
                INSERT INTO discogs_credit
                    (
                        source_type,
                        source_id,
                        discogs_master_id,
                        track_position,
                        track_title,
                        discogs_artist_id,
                        artist_name,
                        artist_anv,
                        raw_role,
                        credit_type,
                        credit_details
                    )
                VALUES
                    (
                        %(source_type)s,
                        %(source_id)s,
                        %(discogs_master_id)s,
                        %(track_position)s,
                        %(track_title)s,
                        %(discogs_artist_id)s,
                        %(artist_name)s,
                        %(artist_anv)s,
                        %(raw_role)s,
                        %(credit_type)s,
                        %(credit_details)s
                    )
                ON CONFLICT (source_type, source_id, track_position, artist_name, raw_role) DO UPDATE
                SET
                    discogs_master_id = EXCLUDED.discogs_master_id,
                    track_title = EXCLUDED.track_title,
                    discogs_artist_id = EXCLUDED.discogs_artist_id,
                    artist_anv = EXCLUDED.artist_anv,
                    credit_type = EXCLUDED.credit_type,
                    credit_details = EXCLUDED.credit_details;
                """,
                {
                    "source_type": source_type,
                    "source_id": source_id,
                    "discogs_master_id": master_id,
                    "track_position": track_position or scope,
                    "track_title": track_title,
                    "discogs_artist_id": artist_id,
                    "artist_name": artist_name,
                    "artist_anv": artist.get("anv"),
                    "raw_role": raw_role,
                    "credit_type": credit_type,
                    "credit_details": credit_details,
                },
            )


def save_videos(cursor, master_id: int, videos: list[dict[str, Any]]):
    for video in videos or []:
        uri = video.get("uri")
        if not uri:
            continue

        cursor.execute(
            """
            INSERT INTO discogs_video
                (discogs_master_id, uri, title, description, duration_seconds, embed)
            VALUES
                (%(discogs_master_id)s, %(uri)s, %(title)s, %(description)s, %(duration_seconds)s, %(embed)s)
            ON CONFLICT (discogs_master_id, uri) DO UPDATE
            SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                duration_seconds = EXCLUDED.duration_seconds,
                embed = EXCLUDED.embed;
            """,
            {
                "discogs_master_id": master_id,
                "uri": uri,
                "title": video.get("title"),
                "description": video.get("description"),
                "duration_seconds": parse_int(video.get("duration")),
                "embed": video.get("embed"),
            },
        )


def split_roles(role: str | None) -> list[str]:
    if not role:
        return []
    return [part.strip() for part in role.split(",") if part.strip()]


def standardize_credit_role(raw_role: str) -> tuple[str, str | None]:
    details_match = role_details.search(raw_role)
    details = details_match.group(1).strip() if details_match is not None else None
    role = role_details.sub("", raw_role).strip().lower()

    if "producer" in role or "production" in role or "program" in role:
        return "producer", details
    if "arranged" in role or "arranger" in role:
        return "arranger", details
    if "written" in role or "composer" in role or "composed" in role or "songwriter" in role or role == "music by":
        return "songwriter", details
    if "lyric" in role:
        return "lyricist", details
    if "master" in role:
        return "mastering", details
    if "mix" in role:
        return "mixing", details
    if "engineer" in role or "recorded" in role:
        return "engineer", details
    if "vocal" in role:
        return "vocals", details

    return normalize_role_key(role) or "unknown", details


def normalize_role_key(value: Any) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", " ", str(value))
    return re.sub(r"\s+", " ", text).strip().lower().replace(" ", "_")


def duration_seconds(duration: str | None) -> int | None:
    if not duration:
        return None

    parts = duration.split(":")
    if not all(part.isdigit() for part in parts):
        return None

    total = 0
    for part in parts:
        total = total * 60 + int(part)
    return total


def primary_image_url(images: list[dict[str, Any]]) -> str | None:
    if not images:
        return None

    for image in images:
        if image.get("type") == "primary":
            return image.get("uri") or image.get("resource_url")

    return images[0].get("uri") or images[0].get("resource_url")


def parse_int(value: Any) -> int | None:
    if value is None or value == "":
        return None

    try:
        return int(value)
    except ValueError:
        return None


def json_param(value):
    return Json(value) if value is not None else None


def json_param_without_urls(value):
    return json_param(without_urls(value))


def without_urls(value):
    if isinstance(value, dict):
        return {
            key: without_urls(item)
            for key, item in value.items()
            if "url" not in key.lower()
        }
    if isinstance(value, list):
        return [without_urls(item) for item in value]
    return value
