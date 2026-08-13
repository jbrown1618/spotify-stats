import re
import unicodedata
from typing import Any

from data.raw import get_connection
from discogs.client import DiscogsApiError, DiscogsClient
from discogs.store import DiscogsStore
from utils.name import short_name


MAX_TRACKS_PER_RUN = 100
ARTIST_RELEASE_PAGES = 2
CANDIDATE_MASTERS = 8
EDITION_MARKERS = {
    "acoustic": re.compile(r"\bacoustic\b"),
    "instrumental": re.compile(r"\binstrumental\b"),
    "japanese": re.compile(r"\b(?:japanese|jp)\b"),
    "live": re.compile(r"\blive\b"),
    "remix": re.compile(r"\bremix(?:ed)?\b"),
}


class DeferredArtistMatch(Exception):
    pass

def save_discogs_data(batch_size: int | None = None, max_tracks: int | None = None):
    client = DiscogsClient()
    requested_batch_size = batch_size if batch_size is not None else max_tracks
    limit = (
        MAX_TRACKS_PER_RUN
        if requested_batch_size is None
        else min(requested_batch_size, MAX_TRACKS_PER_RUN)
    )

    if limit <= 0:
        print(f"Skipping Discogs data fetch because batch size is {limit}")
        return

    with get_connection() as conn:
        cursor = conn.cursor()
        store = DiscogsStore(cursor)
        tracks = store.fetch_unfetched_tracks(limit)
        print(f"Fetching Discogs data for {len(tracks)} tracks, capped at {limit}")

        for track_number, track in enumerate(tracks, start=1):
            print(
                f"Processing Discogs track {track_number}/{len(tracks)}: "
                f"{track['artist_names'][0]} - {track['track_name']}",
                flush=True,
            )
            if not process_track_safely(store, client, track):
                conn.rollback()
                continue
            print(
                f"Committing Discogs records for track {track_number}/{len(tracks)}: "
                f"{track['track_uri']}",
                flush=True,
            )
            conn.commit()


def process_track_safely(
    store: DiscogsStore,
    client: DiscogsClient,
    track: dict[str, Any],
) -> bool:
    try:
        process_track(store, client, track)
    except DiscogsApiError as error:
        print(
            f"Skipping Discogs track {track['track_uri']} after API failure: {error}",
            flush=True,
        )
        return False
    return True


def process_track(store: DiscogsStore, client: DiscogsClient, track: dict[str, Any]):
    print(
        f"Matching primary artist for {track['artist_names'][0]} - {track['track_name']} "
        f"({track['stream_count']} streams)",
        flush=True,
    )
    try:
        discogs_artist_id = match_primary_artist(store, client, track)
    except DeferredArtistMatch as error:
        print(f"Deferring Discogs track {track['track_uri']}: {error}", flush=True)
        return
    if discogs_artist_id is None:
        print(f"No artist match; marking track unmatchable: {track['track_uri']}", flush=True)
        store.mark_unmatchable_track(track["track_uri"], track["track_name"], "No Discogs artist match")
        return

    print(
        f"Finding Discogs master candidates for artist {discogs_artist_id} and track "
        f"{track['track_name']}",
        flush=True,
    )
    matches = find_track_matches(client, discogs_artist_id, track)
    if len(matches) == 0:
        print(f"No master match; marking track unmatchable: {track['track_uri']}", flush=True)
        store.mark_unmatchable_track(track["track_uri"], track["track_name"], "No matching Discogs master track")
        return

    match = matches[0]
    master_id = int(match["master"]["id"])
    if store.has_master(master_id):
        print(
            f"Reusing saved Discogs master {master_id} for {track['track_uri']}",
            flush=True,
        )
    else:
        print(
            f"Saving matched Discogs master {master_id} and credits for "
            f"{track['track_uri']} (score {match['score']})",
            flush=True,
        )
        store.save_master(match["master"])
    save_main_release(store, client, match["master"])
    print(
        f"Saving Spotify track mapping to Discogs master {master_id}",
        flush=True,
    )
    store.save_track_mapping(
        track["track_uri"],
        master_id,
        match["track"].get("position") or "",
        match["track"]["title"],
        match["score"],
        "artist-candidates-track-score",
    )
    if album_match_score(track, match["master"]) >= 35:
        print(
            f"Saving Spotify album mapping to Discogs master {master_id}",
            flush=True,
        )
        store.save_album_mapping(
            track["album_uri"],
            master_id,
            album_match_score(track, match["master"]),
            "album-title-match",
        )


def match_primary_artist(store: DiscogsStore, client: DiscogsClient, track: dict[str, Any]) -> int | None:
    spotify_artist_uri = track["artist_uris"][0]
    artist_name = track["artist_names"][0]

    existing_artist_id = store.matched_discogs_artist_id(spotify_artist_uri)
    if existing_artist_id is not None:
        return existing_artist_id

    if store.is_unmatchable_artist(spotify_artist_uri):
        return None

    results = list(client.search(q=artist_name, type="artist", limit=10))
    target = normalize_name(artist_name)
    matches = [
        result
        for result in results
        if result.get("type") == "artist" and normalize_name(result.get("title")) == target
    ]

    if len(matches) == 0:
        store.mark_unmatchable_artist(spotify_artist_uri, artist_name, "No exact Discogs artist match")
        return None

    unique_matches = {int(match["id"]): match for match in matches}
    match_method = "artist-search-exact-name"
    confidence = 100
    if len(unique_matches) > 1:
        evidence = {
            artist_id: artist_release_evidence(client, artist_id, track)
            for artist_id in unique_matches
        }
        best_score = max(evidence.values())
        evidence_matches = [
            artist_id
            for artist_id, score in evidence.items()
            if score == best_score and score > 0
        ]
        if len(evidence_matches) != 1:
            raise DeferredArtistMatch(
                f"multiple exact artist results for {artist_name} without unique release evidence"
            )
        discogs_artist_id = evidence_matches[0]
        match_method = "artist-search-release-evidence"
        confidence = 90
    else:
        discogs_artist_id = next(iter(unique_matches))

    selected_result = unique_matches[discogs_artist_id]
    print(
        f"Matched Discogs artist search result {discogs_artist_id} "
        f"({selected_result.get('title')}) to Spotify artist {artist_name} "
        f"using {match_method}",
        flush=True,
    )
    artist = client.artist(discogs_artist_id)
    save_artist_with_member_profiles(store, client, artist)
    store.save_artist_mapping(spotify_artist_uri, discogs_artist_id, confidence, match_method)
    return discogs_artist_id


def artist_release_evidence(
    client: DiscogsClient,
    discogs_artist_id: int,
    track: dict[str, Any],
) -> int:
    best_score = 0
    for release in client.artist_releases(
        discogs_artist_id,
        max_pages=ARTIST_RELEASE_PAGES,
    ):
        if release.get("role") not in {None, "Main"}:
            continue
        best_score = max(best_score, candidate_release_match_score(track, release))
    return best_score


def find_track_matches(
    client: DiscogsClient,
    discogs_artist_id: int,
    track: dict[str, Any],
) -> list[dict[str, Any]]:
    candidate_ids = candidate_master_ids(client, discogs_artist_id, track)
    matches: list[dict[str, Any]] = []

    for candidate_id in candidate_ids:
        try:
            master = client.master(candidate_id)
        except DiscogsApiError as error:
            print(f"Skipping Discogs master {candidate_id}: {error}")
            continue

        match = best_track_match(track, master)
        if match is not None and match["score"] >= 75:
            matches.append(match)

    matches.sort(key=lambda match: match["score"], reverse=True)
    if matches:
        match = matches[0]
        print(
            f"Matched Discogs master result {match['master']['id']} "
            f"({match['master'].get('title')}) track "
            f"{match['track'].get('position') or '?'} ({match['track'].get('title')}) "
            f"to Spotify track {track['track_name']} as the best result "
            f"(score {match['score']})",
            flush=True,
        )
    return matches[:1]


def candidate_master_ids(client: DiscogsClient, discogs_artist_id: int, track: dict[str, Any]) -> list[int]:
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
        max_pages=ARTIST_RELEASE_PAGES,
    ):
        if release.get("type") != "master":
            continue
        if release.get("role") not in {None, "Main"}:
            continue
        if candidate_release_matches(track, release):
            add_candidate(release.get("id"))

    for query in [track["album_name"], track["track_name"]]:
        results = client.search(
            q=query,
            artist=track["artist_names"][0],
            type="master",
            limit=10,
        )
        for result in results:
            add_candidate(result.get("master_id") or result.get("id"))

    return candidate_ids[:CANDIDATE_MASTERS]


def candidate_release_matches(track: dict[str, Any], release: dict[str, Any]) -> bool:
    return candidate_release_match_score(track, release) > 0


def candidate_release_match_score(track: dict[str, Any], release: dict[str, Any]) -> int:
    title = normalize_name(release_title(release.get("title", "")))
    album = normalize_name(track["album_name"])
    track_name = normalize_name(track["track_name"])
    short_track = normalize_name(short_name(track["track_name"]))

    if title == album:
        score = 4
    elif title in {track_name, short_track}:
        score = 3
    elif contains_either(title, album):
        score = 2
    elif contains_either(title, track_name) or contains_either(title, short_track):
        score = 1
    else:
        return 0

    if year_matches(track["album_release_date"], release.get("year")):
        score += 1
    return score


def best_track_match(track: dict[str, Any], master: dict[str, Any]) -> dict[str, Any] | None:
    best_match = None
    for discogs_track in master.get("tracklist", []) or []:
        if discogs_track.get("type_") != "track":
            continue

        score = track_match_score(track, master, discogs_track)
        if best_match is None or score > best_match["score"]:
            best_match = {
                "master": master,
                "track": discogs_track,
                "score": score,
            }

    return best_match


def track_match_score(track: dict[str, Any], master: dict[str, Any], discogs_track: dict[str, Any]) -> int:
    score = 0
    spotify_track = normalize_name(track["track_name"])
    spotify_short_track = normalize_name(short_name(track["track_name"]))
    discogs_track_title = normalize_name(discogs_track.get("title"))
    spotify_album = normalize_name(track["album_name"])
    discogs_master = normalize_name(master.get("title"))

    if discogs_track_title in {spotify_track, spotify_short_track}:
        score += 60
    elif contains_either(discogs_track_title, spotify_track) or contains_either(discogs_track_title, spotify_short_track):
        score += 25

    duration_score = duration_match_score(track["duration_ms"], discogs_track.get("duration"))
    score += duration_score

    if discogs_master == spotify_album:
        score += 35
    elif contains_either(discogs_master, spotify_album):
        score += 15
    elif discogs_master in {spotify_track, spotify_short_track}:
        score += 20

    if year_matches(track["album_release_date"], master.get("year")):
        score += 10

    if master_artist_matches(track, master):
        score += 10

    if discogs_track.get("extraartists"):
        score += 20

    return score - edition_mismatch_penalty(track, master, discogs_track)


def edition_mismatch_penalty(
    track: dict[str, Any],
    master: dict[str, Any],
    discogs_track: dict[str, Any],
) -> int:
    spotify_markers = edition_markers(f"{track['album_name']} {track['track_name']}")
    discogs_markers = edition_markers(
        f"{master.get('title', '')} {discogs_track.get('title', '')}"
    )
    return 40 if spotify_markers != discogs_markers else 0


def edition_markers(value: str) -> set[str]:
    normalized = normalize_name(value)
    return {
        marker
        for marker, pattern in EDITION_MARKERS.items()
        if pattern.search(normalized)
    }


def album_match_score(track: dict[str, Any], master: dict[str, Any]) -> int:
    spotify_album = normalize_name(track["album_name"])
    discogs_master = normalize_name(master.get("title"))

    if discogs_master == spotify_album:
        return 100
    if contains_either(discogs_master, spotify_album):
        return 60
    return 0


def save_main_release(store: DiscogsStore, client: DiscogsClient, master: dict[str, Any]):
    master_id = int(master["id"])
    main_release_id = parse_int(master.get("main_release") or master.get("main_release_id"))
    if main_release_id is None:
        return
    if store.has_release(main_release_id):
        print(
            f"Reusing saved Discogs release {main_release_id} for master {master_id}",
            flush=True,
        )
        return

    print(f"Fetching and saving main release for master {master_id}", flush=True)
    release = client.release(main_release_id)
    store.save_release(release, master_id)


def save_artist_with_member_profiles(store: DiscogsStore, client: DiscogsClient, artist: dict[str, Any]):
    store.save_artist(artist)
    group_artist_id = int(artist["id"])
    store.delete_artist_memberships(group_artist_id)

    for member in artist.get("members", []) or []:
        member_artist_id = parse_int(member.get("id"))
        if member_artist_id is None or member_artist_id <= 0:
            continue

        try:
            member_artist = client.artist(member_artist_id)
        except DiscogsApiError as error:
            print(f"Skipping Discogs member artist {member_artist_id}: {error}")
            continue

        store.save_artist(member_artist)
        store.save_artist_membership(group_artist_id, member_artist_id, member.get("active"))
        spotify_artist_uri = store.unique_spotify_artist_uri_for_discogs_name(
            member_artist["name"],
            member_artist_id,
        )
        if spotify_artist_uri is not None:
            store.save_artist_mapping(
                spotify_artist_uri,
                member_artist_id,
                90,
                "group-member-exact-name",
            )


def normalize_name(value: Any) -> str:
    if value is None:
        return ""

    text = DiscogsStore.strip_artist_disambiguation(value)
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


def master_artist_matches(track: dict[str, Any], master: dict[str, Any]) -> bool:
    spotify_artists = {normalize_name(name) for name in track["artist_names"]}
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


if __name__ == '__main__':
    save_discogs_data(5, 5)