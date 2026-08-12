from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from data.raw import get_connection
from discogs.client import DiscogsApiError, DiscogsClient
from discogs.store import (
    SpotifyTrack,
    fetch_unfetched_tracks,
    is_unmatchable_artist,
    mark_unmatchable_artist,
    mark_unmatchable_track,
    matched_discogs_artist_id,
    save_album_mapping,
    save_artist,
    save_artist_mapping,
    save_master,
    save_release,
    save_track_mapping,
)
from utils.name import short_name
from utils.settings import (
    discogs_artist_release_pages,
    discogs_candidate_masters,
    discogs_max_tracks_per_run,
)


artist_disambiguation = re.compile(r"\s+\(\d+\)$")


@dataclass
class DiscogsTrackMatch:
    master: dict[str, Any]
    track: dict[str, Any]
    score: int


def save_discogs_data(batch_size: int | None = None, max_tracks: int | None = None):
    client = DiscogsClient()
    configured_batch_size = discogs_max_tracks_per_run()
    requested_batch_size = batch_size if batch_size is not None else max_tracks
    limit = (
        configured_batch_size
        if requested_batch_size is None
        else min(requested_batch_size, configured_batch_size)
    )

    if limit <= 0:
        print(f"Skipping Discogs data fetch because batch size is {limit}")
        return

    with get_connection() as conn:
        cursor = conn.cursor()
        tracks = fetch_unfetched_tracks(cursor, limit)
        print(f"Fetching Discogs data for {len(tracks)} tracks, capped at {limit}")

        for track in tracks:
            process_track(cursor, client, track)
            conn.commit()

def process_track(cursor, client: DiscogsClient, track: SpotifyTrack):
    print(
        f"Fetching Discogs candidates for {track.artist_names[0]} - {track.track_name} "
        f"({track.stream_count} streams)"
    )
    discogs_artist_id = match_primary_artist(cursor, client, track)
    if discogs_artist_id is None:
        mark_unmatchable_track(cursor, track.track_uri, track.track_name, "No Discogs artist match")
        return

    matches = find_track_matches(cursor, client, discogs_artist_id, track)
    if len(matches) == 0:
        mark_unmatchable_track(cursor, track.track_uri, track.track_name, "No matching Discogs master track")
        return

    for match in matches:
        save_master(cursor, match.master)
        save_main_release(cursor, client, match.master)
        save_track_mapping(
            cursor,
            track.track_uri,
            int(match.master["id"]),
            match.track.get("position") or "",
            match.track["title"],
            match.score,
            "artist-candidates-track-score",
        )
        if album_match_score(track, match.master) >= 35:
            save_album_mapping(
                cursor,
                track.album_uri,
                int(match.master["id"]),
                album_match_score(track, match.master),
                "album-title-match",
            )


def match_primary_artist(cursor, client: DiscogsClient, track: SpotifyTrack) -> int | None:
    spotify_artist_uri = track.artist_uris[0]
    artist_name = track.artist_names[0]

    existing_artist_id = matched_discogs_artist_id(cursor, spotify_artist_uri)
    if existing_artist_id is not None:
        return existing_artist_id

    if is_unmatchable_artist(cursor, spotify_artist_uri):
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
    save_artist_mapping(cursor, spotify_artist_uri, discogs_artist_id, 100, "artist-search-exact-name")
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


def save_main_release(cursor, client: DiscogsClient, master: dict[str, Any]):
    master_id = int(master["id"])
    main_release_id = parse_int(master.get("main_release") or master.get("main_release_id"))
    if main_release_id is None:
        return

    try:
        release = client.release(main_release_id)
    except DiscogsApiError as error:
        print(f"Skipping Discogs release {main_release_id}: {error}")
        return

    save_release(cursor, release, master_id)


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


def parse_int(value: Any) -> int | None:
    if value is None or value == "":
        return None

    try:
        return int(value)
    except ValueError:
        return None
