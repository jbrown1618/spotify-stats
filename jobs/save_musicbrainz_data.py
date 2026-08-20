from typing import Any

import musicbrainzngs as mb

from data.database import get_connection
from musicbrainz.store import MusicBrainzStore
from utils.settings import (
    musicbrainz_contact,
    musicbrainz_max_artists_per_run,
    musicbrainz_max_tracks_per_run,
    musicbrainz_retry_days,
    musicbrainz_useragent,
    musicbrainz_version,
)


MUSICBRAINZ_ERRORS = (mb.WebServiceError, mb.ResponseError, mb.NetworkError)
IGNORED_CREDIT_TYPES = {
    "audio",
    "conductor",
    "creative direction",
    "misc",
    "phonographic copyright",
}
SONGWRITER_ROLES = {"composer", "writer"}
PRODUCER_ROLES = {
    "editor",
    "engineer",
    "mix",
    "producer",
    "programming",
    "recording",
    "remixer",
}
ARRANGER_ROLES = {
    "arranger",
    "instrument arranger",
    "orchestrator",
    "vocal arranger",
}
PUNCTUATION_REPLACEMENTS = {
    "-": {"\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015"},
    "'": {"\u2018", "\u2019"},
    '"': {"\u201c", "\u201d"},
}


def save_musicbrainz_data(
    max_tracks: int | None = None,
    max_artists: int | None = None,
):
    limit = (
        musicbrainz_max_tracks_per_run()
        if max_tracks is None
        else max_tracks
    )
    configured_artist_limit = musicbrainz_max_artists_per_run()
    artist_limit = (
        configured_artist_limit
        if max_artists is None
        else min(max_artists, configured_artist_limit)
    )
    if limit <= 0:
        print(f"Skipping MusicBrainz data fetch because track limit is {limit}")
        return {
            "tracks_selected": 0,
            "tracks_completed": 0,
            "artists_saved": 0,
            "api_failures": 0,
        }

    mb.set_useragent(
        musicbrainz_useragent(),
        musicbrainz_version(),
        musicbrainz_contact(),
    )
    committed_artist_mbids: set[str] = set()
    tracks_completed = 0
    api_failures = 0

    with get_connection() as conn:
        cursor = conn.cursor()
        store = MusicBrainzStore(cursor, musicbrainz_retry_days())
        tracks = store.fetch_unfetched_tracks(limit)
        print(f"Fetching MusicBrainz data for {len(tracks)} tracks, capped at {limit}")

        for track_number, track in enumerate(tracks, start=1):
            print(
                f"Processing MusicBrainz track {track_number}/{len(tracks)}: "
                f"{track['artist_names'][0]} - {track['track_name']} "
                f"({track['stream_count']} streams, ISRC {track['isrc']})",
                flush=True,
            )
            processed_artist_mbids: set[str] = set()
            try:
                process_track(
                    store,
                    track,
                    committed_artist_mbids,
                    processed_artist_mbids,
                )
            except MUSICBRAINZ_ERRORS as error:
                print(
                    f"Skipping MusicBrainz track {track['track_uri']} after API failure: "
                    f"{error}",
                    flush=True,
                )
                conn.rollback()
                api_failures += 1
                continue

            conn.commit()
            tracks_completed += 1
            committed_artist_mbids.update(processed_artist_mbids)
            print(
                f"Committed MusicBrainz records for {track['track_uri']}",
                flush=True,
            )

        match_additional_liked_artists(
            store,
            conn,
            committed_artist_mbids,
            max_artists=artist_limit,
        )

    return {
        "tracks_selected": len(tracks),
        "tracks_completed": tracks_completed,
        "artists_saved": len(committed_artist_mbids),
        "api_failures": api_failures,
    }


def process_track(
    store: MusicBrainzStore,
    track: dict[str, Any],
    committed_artist_mbids: set[str] | None = None,
    processed_artist_mbids: set[str] | None = None,
):
    if committed_artist_mbids is None:
        committed_artist_mbids = set()
    if processed_artist_mbids is None:
        processed_artist_mbids = set()

    isrc = track["isrc"].upper()
    print(f"Looking up MusicBrainz recording by ISRC {isrc}", flush=True)
    isrc_result = mb.get_recordings_by_isrc(isrc)
    candidates = isrc_result.get("isrc", {}).get("recording-list", [])
    print(
        f"MusicBrainz returned {len(candidates)} recording candidate(s) for ISRC {isrc}",
        flush=True,
    )
    recording_match = select_recording_candidate(track["track_name"], candidates)
    if recording_match is None:
        store.mark_unfetchable_isrc(isrc, "No MusicBrainz recording for ISRC")
        print(f"No MusicBrainz recording for ISRC {isrc}", flush=True)
        return

    recording = mb.get_recording_by_id(
        recording_match["id"],
        includes=["artist-rels", "work-rels", "work-level-rels"],
    )["recording"]
    primary_work = next(
        (
            relation["work"]
            for relation in recording.get("work-relation-list", [])
            if relation["type"] == "performance"
        ),
        None,
    )
    recording["title"] = normalize_punctuation(recording["title"])
    store.save_recording(recording, (primary_work or {}).get("language"))

    artist_relations = recording.get("artist-relation-list", []) + (
        primary_work or {}
    ).get("artist-relation-list", [])
    credits = recording_credits(artist_relations)
    store.replace_recording_credits(recording["id"], credits)
    credit_counts: dict[str, int] = {}
    for credit in credits:
        credit_type = credit["credit_type"]
        credit_counts[credit_type] = credit_counts.get(credit_type, 0) + 1
    credit_summary = ", ".join(
        f"{credit_type}={count}"
        for credit_type, count in sorted(credit_counts.items())
    )
    print(
        f"Saved {len(credits)} MusicBrainz credit(s) for recording "
        f"{recording['id']} ({credit_summary or 'none'})",
        flush=True,
    )
    if not credits:
        store.mark_unfetchable_isrc(isrc, "MusicBrainz recording has no credits")
        print(
            f"Recording {recording['id']} has no credits; retrying ISRC {isrc} "
            f"after {musicbrainz_retry_days()} days",
            flush=True,
        )
    save_artist_graph(
        store,
        {credit["artist_mbid"] for credit in credits},
        committed_artist_mbids,
        processed_artist_mbids,
    )
    store.save_track_mapping(track["track_uri"], recording["id"])
    print(
        f"Matched MusicBrainz recording {recording['id']} ({recording['title']}) "
        f"to {track['track_uri']}",
        flush=True,
    )


def select_recording_candidate(
    track_name: str,
    candidates: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    target = normalize_artist_name(track_name)
    title_matches = [
        candidate
        for candidate in candidates
        if normalize_artist_name(candidate.get("title", "")) == target
    ]
    if len(title_matches) == 1:
        return title_matches[0]

    print(
        f"ISRC returned {len(candidates)} recordings without a unique title match; "
        f"using {candidates[0]['id']}",
        flush=True,
    )
    return candidates[0]


def recording_credits(artist_relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    credits = []
    for relation in artist_relations:
        if "assistant" in relation.get("attribute-list", []):
            continue

        credit_type = standardize_credit_type(relation["type"])
        if credit_type is None:
            continue
        credits.append(
            {
                "artist_mbid": relation["artist"]["id"],
                "raw_role": relation["type"],
                "credit_type": credit_type,
                "credit_details": ";".join(relation.get("attribute-list", [])),
            }
        )
    return credits


def standardize_credit_type(credit_type: str) -> str | None:
    if credit_type in IGNORED_CREDIT_TYPES:
        return None
    if credit_type in SONGWRITER_ROLES:
        return "songwriter"
    if credit_type in PRODUCER_ROLES:
        return "producer"
    if credit_type in ARRANGER_ROLES:
        return "arranger"
    return credit_type


def save_artist_graph(
    store: MusicBrainzStore,
    initial_mbids: set[str],
    committed_artist_mbids: set[str],
    processed_artist_mbids: set[str],
):
    artist_queue = set(initial_mbids) - committed_artist_mbids - processed_artist_mbids
    while artist_queue:
        artist_mbid = artist_queue.pop()
        if store.has_artist(artist_mbid):
            print(f"Reusing saved MusicBrainz artist {artist_mbid}", flush=True)
            processed_artist_mbids.add(artist_mbid)
            continue

        artist = mb.get_artist_by_id(
            artist_mbid,
            includes=["artist-rels", "aliases"],
        )["artist"]
        print(f"Fetching MusicBrainz artist {artist['name']}", flush=True)
        save_artist(store, artist)
        processed_artist_mbids.add(artist_mbid)

        relationships, related_mbids = artist_relationships(store, artist)
        store.save_artist_relationships(relationships)
        print(
            f"Saved MusicBrainz artist {artist_mbid}: "
            f"aliases={len(artist.get('alias-list', []))}, "
            f"relationships={len(relationships)}, queued_related={len(related_mbids)}",
            flush=True,
        )
        artist_queue.update(
            related_mbids - committed_artist_mbids - processed_artist_mbids
        )


def save_artist(store: MusicBrainzStore, artist: dict[str, Any]):
    artist_mbid = artist["id"]
    store.save_artist(
        {
            "artist_mbid": artist_mbid,
            "artist_mb_name": normalize_punctuation(artist["name"]),
            "artist_sort_name": normalize_punctuation(artist["sort-name"]),
            "artist_disambiguation": artist.get("disambiguation"),
            "artist_type": artist.get("type", "Unknown"),
            "artist_area": artist.get("area", {}).get("name"),
            "artist_birthplace": artist.get("begin-area", {}).get("name"),
            "artist_start_date": artist.get("life-span", {}).get("begin"),
            "artist_end_date": artist.get("life-span", {}).get("end"),
            "artist_gender": artist.get("gender"),
        }
    )
    aliases = [normalize_alias(alias) for alias in artist.get("alias-list", [])]
    store.replace_artist_aliases(artist_mbid, aliases)

    names = [artist["name"], artist["sort-name"]]
    names.extend(alias["alias_name"] for alias in aliases)
    matching_artist_uris = store.matching_spotify_artists(names)
    if len(matching_artist_uris) == 1:
        store.save_artist_mapping(matching_artist_uris[0], artist_mbid)
        print(
            f"Mapped Spotify artist {matching_artist_uris[0]} to MusicBrainz "
            f"artist {artist_mbid} using canonical name or alias",
            flush=True,
        )
    elif len(matching_artist_uris) > 1:
        print(
            f"Multiple Spotify artists match MusicBrainz artist {artist['name']}; "
            "not saving an automatic mapping",
            flush=True,
        )


def normalize_alias(alias: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(alias, str):
        return {
            "alias_name": normalize_punctuation(alias),
            "sort_name": "",
            "locale": "",
            "alias_type": "",
            "primary_for_locale": False,
        }
    return {
        "alias_name": normalize_punctuation(alias["alias"]),
        "sort_name": normalize_punctuation(alias.get("sort-name", "")),
        "locale": alias.get("locale") or "",
        "alias_type": alias.get("type") or "",
        "primary_for_locale": alias.get("primary") in {True, "primary"},
    }


def artist_relationships(
    store: MusicBrainzStore,
    artist: dict[str, Any],
) -> tuple[list[dict[str, str]], set[str]]:
    relationships = []
    related_mbids = set()
    for relation in artist.get("artist-relation-list", []):
        if not should_record_relationship(store, artist, relation):
            continue

        other_mbid = relation["artist"]["id"]
        if relation["direction"] == "forward":
            artist_mbid, related_mbid = artist["id"], other_mbid
        else:
            artist_mbid, related_mbid = other_mbid, artist["id"]
        relationships.append(
            {
                "artist_mbid": artist_mbid,
                "other_mbid": related_mbid,
                "relationship_type": relation["type"],
            }
        )
        related_mbids.add(other_mbid)
    return relationships, related_mbids


def should_record_relationship(
    store: MusicBrainzStore,
    artist: dict[str, Any],
    relation: dict[str, Any],
) -> bool:
    relationship_type = relation["type"]
    direction = relation["direction"]
    artist_type = artist.get("type", "Unknown").casefold()
    if relationship_type in {"artist rename", "is person"}:
        return True
    if artist_type == "group" and relationship_type == "member of band":
        return direction == "backward"

    matching_artist_uris = store.matching_spotify_artists(
        [relation["artist"]["name"]]
    )
    if relationship_type == "subgroup":
        return len(matching_artist_uris) == 1
    return (
        artist_type == "person"
        and relationship_type == "member of band"
        and direction == "forward"
        and len(matching_artist_uris) == 1
    )


def match_additional_liked_artists(
    store: MusicBrainzStore,
    conn,
    committed_artist_mbids: set[str],
    max_artists: int | None = None,
):
    spotify_artists = store.fetch_unmatched_liked_artists()
    total_artists = len(spotify_artists)
    if max_artists is not None:
        spotify_artists = spotify_artists[:max(0, max_artists)]
    print(
        f"Matching {len(spotify_artists)} of {total_artists} additional liked "
        "Spotify artist(s) to MusicBrainz",
        flush=True,
    )
    for artist_number, spotify_artist in enumerate(spotify_artists, start=1):
        print(
            f"Processing MusicBrainz artist {artist_number}/{len(spotify_artists)}: "
            f"{spotify_artist['artist_name']}",
            flush=True,
        )
        try:
            results = mb.search_artists(spotify_artist["artist_name"], limit=2).get(
                "artist-list", []
            )
            perfect_matches = [
                result
                for result in results
                if float(result.get("ext:score", 0)) == 100
            ]
            if len(perfect_matches) != 1:
                reason = (
                    "No exact MusicBrainz artist match"
                    if not perfect_matches
                    else "Multiple exact MusicBrainz artist matches"
                )
                store.mark_unmatchable_artist(
                    spotify_artist["artist_uri"],
                    spotify_artist["artist_name"],
                    reason,
                )
                print(
                    f"Deferring Spotify artist {spotify_artist['artist_uri']}: {reason}",
                    flush=True,
                )
                conn.commit()
                continue

            artist_mbid = perfect_matches[0]["id"]
            processed_artist_mbids: set[str] = set()
            save_artist_graph(
                store,
                {artist_mbid},
                committed_artist_mbids,
                processed_artist_mbids,
            )
            store.save_artist_mapping(spotify_artist["artist_uri"], artist_mbid)
            conn.commit()
            committed_artist_mbids.update(processed_artist_mbids)
            print(
                f"Committed Spotify artist {spotify_artist['artist_uri']} mapping "
                f"to MusicBrainz artist {artist_mbid}",
                flush=True,
            )
        except MUSICBRAINZ_ERRORS as error:
            print(
                f"Skipping MusicBrainz artist {spotify_artist['artist_name']} after "
                f"API failure: {error}",
                flush=True,
            )
            conn.rollback()


def normalize_punctuation(name: str) -> str:
    normalized = name
    for replacement, values in PUNCTUATION_REPLACEMENTS.items():
        for value in values:
            normalized = normalized.replace(value, replacement)
    return normalized


def normalize_artist_name(name: str) -> str:
    return normalize_punctuation(name.strip().casefold())


if __name__ == "__main__":
    save_musicbrainz_data()
