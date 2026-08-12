from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from psycopg2.extras import Json, RealDictCursor

from data.raw import get_connection
from discogs.client import DiscogsApiError, DiscogsClient
from utils.name import short_name
from utils.settings import (
    discogs_artist_release_pages,
    discogs_candidate_masters,
    discogs_max_tracks_per_run,
)


artist_disambiguation = re.compile(r"\s+\(\d+\)$")
role_details = re.compile(r"\[(.+)\]")


@dataclass
class SpotifyTrack:
    track_uri: str
    track_name: str
    duration_ms: int | None
    album_uri: str
    album_name: str
    album_release_date: str | None
    artist_uris: list[str]
    artist_names: list[str]


@dataclass
class DiscogsTrackMatch:
    master: dict[str, Any]
    track: dict[str, Any]
    score: int


def save_discogs_data(max_tracks: int | None = None):
    client = DiscogsClient()
    limit = max_tracks or discogs_max_tracks_per_run()

    with get_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        tracks = unfetched_tracks(cursor, limit)
        print(f"Fetching Discogs data for {len(tracks)} tracks")

        for track in tracks:
            process_track(cursor, client, track)
            conn.commit()


def unfetched_tracks(cursor, limit: int) -> list[SpotifyTrack]:
    cursor.execute(
        """
        SELECT
            t.uri AS track_uri,
            t.name AS track_name,
            t.duration_ms,
            t.album_uri,
            al.name AS album_name,
            al.release_date AS album_release_date,
            ARRAY_AGG(a.uri ORDER BY ta.artist_index) AS artist_uris,
            ARRAY_AGG(a.name ORDER BY ta.artist_index) AS artist_names
        FROM track t
            INNER JOIN album al ON t.album_uri = al.uri
            INNER JOIN track_artist ta ON t.uri = ta.track_uri
            INNER JOIN artist a ON ta.artist_uri = a.uri
            LEFT JOIN liked_track lt ON t.uri = lt.track_uri
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
            lt.track_uri
        ORDER BY
            (lt.track_uri IS NOT NULL) DESC,
            al.release_date DESC NULLS LAST,
            t.name
        LIMIT %(limit)s;
        """,
        {"limit": limit},
    )
    return [
        SpotifyTrack(
            track_uri=row["track_uri"],
            track_name=row["track_name"],
            duration_ms=row["duration_ms"],
            album_uri=row["album_uri"],
            album_name=row["album_name"],
            album_release_date=row["album_release_date"],
            artist_uris=row["artist_uris"],
            artist_names=row["artist_names"],
        )
        for row in cursor.fetchall()
    ]


def process_track(cursor, client: DiscogsClient, track: SpotifyTrack):
    print(f"Fetching Discogs candidates for {track.artist_names[0]} - {track.track_name}")
    discogs_artist_id = match_primary_artist(cursor, client, track)
    if discogs_artist_id is None:
        mark_unmatchable_track(cursor, track, "No Discogs artist match")
        return

    matches = find_track_matches(cursor, client, discogs_artist_id, track)
    if len(matches) == 0:
        mark_unmatchable_track(cursor, track, "No matching Discogs master track")
        return

    for match in matches:
        save_master(cursor, client, match.master)
        map_track(cursor, track, match)
        if album_match_score(track, match.master) >= 35:
            map_album(cursor, track, match)


def match_primary_artist(cursor, client: DiscogsClient, track: SpotifyTrack) -> int | None:
    spotify_artist_uri = track.artist_uris[0]
    artist_name = track.artist_names[0]

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
    if existing is not None:
        return existing["discogs_artist_id"]

    cursor.execute(
        """
        SELECT 1
        FROM discogs_unmatchable_artist
        WHERE spotify_artist_uri = %(spotify_artist_uri)s;
        """,
        {"spotify_artist_uri": spotify_artist_uri},
    )
    if cursor.fetchone() is not None:
        return None

    results = list(client.search(q=artist_name, type="artist", limit=10))
    target = normalize_name(artist_name)
    matches = [
        result
        for result in results
        if result.get("type") == "artist" and normalize_name(result.get("title")) == target
    ]

    if len(matches) == 0:
        mark_unmatchable_artist(cursor, spotify_artist_uri, artist_name, "No exact Discogs artist match")
        return None

    if len({match["id"] for match in matches}) > 1:
        mark_unmatchable_artist(cursor, spotify_artist_uri, artist_name, "Multiple exact Discogs artist matches")
        return None

    discogs_artist_id = int(matches[0]["id"])
    artist = client.artist(discogs_artist_id)
    save_artist(cursor, artist)
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
            "confidence": 100,
            "match_method": "artist-search-exact-name",
        },
    )
    return discogs_artist_id


def find_track_matches(
    _,
    client: DiscogsClient,
    discogs_artist_id: int,
    track: SpotifyTrack,
) -> list[DiscogsTrackMatch]:
    candidate_ids = candidate_master_ids(client, discogs_artist_id, track)
    matches: list[DiscogsTrackMatch] = []

    for candidate_id in candidate_ids:
        try:
            master = client.master(candidate_id)
        except DiscogsApiError as error:
            print(f"Skipping Discogs master {candidate_id}: {error}")
            continue

        match = best_track_match(track, master)
        if match is not None and match.score >= 75:
            matches.append(match)

    matches.sort(key=lambda match: match.score, reverse=True)
    return matches[:3]


def candidate_master_ids(client: DiscogsClient, discogs_artist_id: int, track: SpotifyTrack) -> list[int]:
    candidate_ids: list[int] = []
    seen: set[int] = set()

    def add_candidate(value):
        candidate_id = parse_int(value)
        if candidate_id is None or candidate_id <= 0 or candidate_id in seen:
            return
        seen.add(candidate_id)
        candidate_ids.append(candidate_id)

    for release in client.artist_releases(
        discogs_artist_id,
        max_pages=discogs_artist_release_pages(),
    ):
        if release.get("type") != "master":
            continue
        if release.get("role") not in {None, "Main"}:
            continue
        if candidate_release_matches(track, release):
            add_candidate(release.get("id"))

    for query in [track.album_name, track.track_name]:
        results = client.search(
            q=query,
            artist=track.artist_names[0],
            type="master",
            limit=10,
        )
        for result in results:
            add_candidate(result.get("master_id") or result.get("id"))

    return candidate_ids[:discogs_candidate_masters()]


def candidate_release_matches(track: SpotifyTrack, release: dict[str, Any]) -> bool:
    title = normalize_name(release_title(release.get("title", "")))
    album = normalize_name(track.album_name)
    track_name = normalize_name(track.track_name)
    short_track = normalize_name(short_name(track.track_name))

    return (
        title in {album, track_name, short_track}
        or contains_either(title, album)
        or contains_either(title, track_name)
        or contains_either(title, short_track)
    )


def best_track_match(track: SpotifyTrack, master: dict[str, Any]) -> DiscogsTrackMatch | None:
    best_match = None
    for discogs_track in master.get("tracklist", []) or []:
        if discogs_track.get("type_") != "track":
            continue

        score = track_match_score(track, master, discogs_track)
        if best_match is None or score > best_match.score:
            best_match = DiscogsTrackMatch(master=master, track=discogs_track, score=score)

    return best_match


def track_match_score(track: SpotifyTrack, master: dict[str, Any], discogs_track: dict[str, Any]) -> int:
    score = 0
    spotify_track = normalize_name(track.track_name)
    spotify_short_track = normalize_name(short_name(track.track_name))
    discogs_track_title = normalize_name(discogs_track.get("title"))
    spotify_album = normalize_name(track.album_name)
    discogs_master = normalize_name(master.get("title"))

    if discogs_track_title in {spotify_track, spotify_short_track}:
        score += 60
    elif contains_either(discogs_track_title, spotify_track) or contains_either(discogs_track_title, spotify_short_track):
        score += 25

    duration_score = duration_match_score(track.duration_ms, discogs_track.get("duration"))
    score += duration_score

    if discogs_master == spotify_album:
        score += 35
    elif contains_either(discogs_master, spotify_album):
        score += 15
    elif discogs_master in {spotify_track, spotify_short_track}:
        score += 20

    if year_matches(track.album_release_date, master.get("year")):
        score += 10

    if master_artist_matches(track, master):
        score += 10

    if discogs_track.get("extraartists"):
        score += 20

    return score


def album_match_score(track: SpotifyTrack, master: dict[str, Any]) -> int:
    spotify_album = normalize_name(track.album_name)
    discogs_master = normalize_name(master.get("title"))

    if discogs_master == spotify_album:
        return 100
    if contains_either(discogs_master, spotify_album):
        return 60
    return 0


def save_master(cursor, client: DiscogsClient, master: dict[str, Any]):
    master_id = int(master["id"] if "id" in master else master["discogs_master_id"])
    main_release_id = parse_int(master.get("main_release") or master.get("main_release_id"))
    cursor.execute(
        """
        INSERT INTO discogs_master
            (discogs_master_id, title, year, main_release_id, data_quality, resource_url, genres, styles, updated_at)
        VALUES
            (
                %(discogs_master_id)s,
                %(title)s,
                %(year)s,
                %(main_release_id)s,
                %(data_quality)s,
                %(resource_url)s,
                %(genres)s,
                %(styles)s,
                CURRENT_TIMESTAMP
            )
        ON CONFLICT (discogs_master_id) DO UPDATE
        SET
            title = EXCLUDED.title,
            year = EXCLUDED.year,
            main_release_id = EXCLUDED.main_release_id,
            data_quality = EXCLUDED.data_quality,
            resource_url = EXCLUDED.resource_url,
            genres = EXCLUDED.genres,
            styles = EXCLUDED.styles,
            updated_at = CURRENT_TIMESTAMP;
        """,
        {
            "discogs_master_id": master_id,
            "title": master["title"],
            "year": parse_int(master.get("year")),
            "main_release_id": main_release_id,
            "data_quality": master.get("data_quality"),
            "resource_url": master.get("resource_url") or f"{DiscogsClient.base_url}/masters/{master_id}",
            "genres": json_param(master.get("genres")),
            "styles": json_param(master.get("styles")),
        },
    )

    save_tracks_and_credits(cursor, "master", master_id, master_id, master.get("tracklist", []))
    save_entity_credits(cursor, "master", master_id, master_id, master.get("extraartists", []))
    save_videos(cursor, master_id, master.get("videos", []))

    if main_release_id is not None:
        try:
            release = client.release(main_release_id)
        except DiscogsApiError as error:
            print(f"Skipping Discogs release {main_release_id}: {error}")
            return

        save_release(cursor, release, master_id)


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
                data_quality,
                resource_url,
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
                %(data_quality)s,
                %(resource_url)s,
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
            data_quality = EXCLUDED.data_quality,
            resource_url = EXCLUDED.resource_url,
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
            "data_quality": release.get("data_quality"),
            "resource_url": release.get("resource_url") or f"{DiscogsClient.base_url}/releases/{release_id}",
            "labels": json_param(release.get("labels")),
            "companies": json_param(release.get("companies")),
            "formats": json_param(release.get("formats")),
            "identifiers": json_param(release.get("identifiers")),
        },
    )

    save_tracks_and_credits(cursor, "release", release_id, master_id, release.get("tracklist", []))
    save_entity_credits(cursor, "release", release_id, master_id, release.get("extraartists", []))


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
                data_quality,
                resource_url,
                primary_image_url,
                urls,
                namevariations,
                members,
                updated_at
            )
        VALUES
            (
                %(discogs_artist_id)s,
                %(name)s,
                %(realname)s,
                %(profile)s,
                %(data_quality)s,
                %(resource_url)s,
                %(primary_image_url)s,
                %(urls)s,
                %(namevariations)s,
                %(members)s,
                CURRENT_TIMESTAMP
            )
        ON CONFLICT (discogs_artist_id) DO UPDATE
        SET
            name = EXCLUDED.name,
            realname = EXCLUDED.realname,
            profile = EXCLUDED.profile,
            data_quality = EXCLUDED.data_quality,
            resource_url = EXCLUDED.resource_url,
            primary_image_url = EXCLUDED.primary_image_url,
            urls = EXCLUDED.urls,
            namevariations = EXCLUDED.namevariations,
            members = EXCLUDED.members,
            updated_at = CURRENT_TIMESTAMP;
        """,
        {
            "discogs_artist_id": artist_id,
            "name": artist["name"],
            "realname": artist.get("realname"),
            "profile": artist.get("profile"),
            "data_quality": artist.get("data_quality"),
            "resource_url": artist.get("resource_url") or f"{DiscogsClient.base_url}/artists/{artist_id}",
            "primary_image_url": primary_image_url(artist.get("images", [])),
            "urls": json_param(artist.get("urls")),
            "namevariations": json_param(artist.get("namevariations")),
            "members": json_param(artist.get("members")),
        },
    )
    save_artist_memberships(cursor, artist_id, artist.get("members", []))


def save_artist_memberships(cursor, group_artist_id: int, members: list[dict[str, Any]]):
    for member in members or []:
        member_id = parse_int(member.get("id"))
        member_name = member.get("name")
        if member_id is None or member_id <= 0 or not member_name:
            continue

        save_minimal_artist(cursor, member)
        cursor.execute(
            """
            INSERT INTO discogs_artist_membership
                (group_discogs_artist_id, member_discogs_artist_id, member_name, active, resource_url)
            VALUES
                (
                    %(group_discogs_artist_id)s,
                    %(member_discogs_artist_id)s,
                    %(member_name)s,
                    %(active)s,
                    %(resource_url)s
                )
            ON CONFLICT (group_discogs_artist_id, member_discogs_artist_id) DO UPDATE
            SET
                member_name = EXCLUDED.member_name,
                active = EXCLUDED.active,
                resource_url = EXCLUDED.resource_url;
            """,
            {
                "group_discogs_artist_id": group_artist_id,
                "member_discogs_artist_id": member_id,
                "member_name": member_name,
                "active": member.get("active"),
                "resource_url": member.get("resource_url"),
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
            (discogs_artist_id, name, resource_url, updated_at)
        VALUES
            (%(discogs_artist_id)s, %(name)s, %(resource_url)s, CURRENT_TIMESTAMP)
        ON CONFLICT (discogs_artist_id) DO UPDATE
        SET
            name = COALESCE(discogs_artist.name, EXCLUDED.name),
            resource_url = COALESCE(discogs_artist.resource_url, EXCLUDED.resource_url),
            updated_at = CURRENT_TIMESTAMP;
        """,
        {
            "discogs_artist_id": artist_id,
            "name": name,
            "resource_url": artist.get("resource_url"),
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
                    (discogs_master_id, position, title, duration, duration_seconds, track_type)
                VALUES
                    (%(discogs_master_id)s, %(position)s, %(title)s, %(duration)s, %(duration_seconds)s, %(track_type)s)
                ON CONFLICT (discogs_master_id, position, title) DO UPDATE
                SET
                    duration = EXCLUDED.duration,
                    duration_seconds = EXCLUDED.duration_seconds,
                    track_type = EXCLUDED.track_type;
                """,
                {
                    "discogs_master_id": master_id,
                    "position": position,
                    "title": title,
                    "duration": track.get("duration"),
                    "duration_seconds": duration_seconds(track.get("duration")),
                    "track_type": track.get("type_"),
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


def map_track(cursor, track: SpotifyTrack, match: DiscogsTrackMatch):
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
            "spotify_track_uri": track.track_uri,
            "discogs_master_id": int(match.master["id"]),
            "discogs_track_position": match.track.get("position") or "",
            "discogs_track_title": match.track["title"],
            "confidence": match.score,
            "match_method": "artist-candidates-track-score",
        },
    )


def map_album(cursor, track: SpotifyTrack, match: DiscogsTrackMatch):
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
            "spotify_album_uri": track.album_uri,
            "discogs_master_id": int(match.master["id"]),
            "confidence": album_match_score(track, match.master),
            "match_method": "album-title-match",
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


def mark_unmatchable_track(cursor, track: SpotifyTrack, reason: str):
    print(f"Could not match Discogs track {track.artist_names[0]} - {track.track_name}: {reason}")
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
            "spotify_track_uri": track.track_uri,
            "track_name": track.track_name,
            "reason": reason,
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

    return normalize_name(role).replace(" ", "_") or "unknown", details


def normalize_name(value: Any) -> str:
    if value is None:
        return ""

    text = str(value)
    text = artist_disambiguation.sub("", text)
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-zA-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def release_title(title: str) -> str:
    if " - " in title:
        return title.split(" - ", 1)[1]
    return title


def contains_either(first: str, second: str) -> bool:
    if not first or not second:
        return False
    return first in second or second in first


def duration_match_score(spotify_duration_ms: int | None, discogs_duration: str | None) -> int:
    spotify_seconds = None if spotify_duration_ms is None else round(spotify_duration_ms / 1000)
    discogs_seconds = duration_seconds(discogs_duration)

    if spotify_seconds is None or discogs_seconds is None:
        return 0

    delta = abs(spotify_seconds - discogs_seconds)
    if delta <= 5:
        return 20
    if delta <= 10:
        return 10
    return 0


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


def year_matches(spotify_release_date: str | None, discogs_year: Any) -> bool:
    if spotify_release_date is None or discogs_year is None:
        return False

    spotify_year = parse_int(spotify_release_date[0:4])
    year = parse_int(discogs_year)
    if spotify_year is None or year is None:
        return False

    return abs(spotify_year - year) <= 1


def master_artist_matches(track: SpotifyTrack, master: dict[str, Any]) -> bool:
    spotify_artists = {normalize_name(name) for name in track.artist_names}
    discogs_artists = {
        normalize_name(artist.get("name"))
        for artist in master.get("artists", []) or []
    }
    return len(spotify_artists.intersection(discogs_artists)) > 0


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
