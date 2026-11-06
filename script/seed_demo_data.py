"""Seed the local database with deterministic data for screenshots and demos."""

import argparse
import random
from datetime import datetime, timedelta
from urllib.parse import quote
from xml.sax.saxutils import escape

from psycopg2.extras import execute_values

from data.database import get_connection
from spotify.store import SpotifyStore
from utils.settings import postgres_url


MIN_YEAR = 2020
TRACK_NAMES = (
    ("Slow Motion", "Paper Moons"),
    ("Glass Houses", "Midnight Radio"),
    ("Wildflower", "Stay a Little"),
    ("Golden", "Halfway Home"),
    ("Satellite", "Open Water"),
    ("Blue Hour", "Soft Landing"),
    ("Daydreaming", "Almost There"),
    ("Little Fires", "Wide Awake"),
)
ARTIST_NAMES = (
    ("Echo Harbor", ("indie pop", "dream pop")),
    ("Velvet Arcade", ("synthpop", "indie pop")),
    ("Mira Sol", ("alternative r&b", "soul")),
    ("Juniper Lane", ("folk pop", "indie folk")),
    ("Northbound", ("indie rock", "alternative rock")),
    ("Luna Vale", ("electronic", "downtempo")),
    ("Paper Satellites", ("dream pop", "electronic")),
    ("Golden Hour Club", ("soul", "pop")),
)
PALETTE = ("#386c72", "#74517d", "#b06b4e", "#446b55", "#525e91", "#a14f68")
LABELS = (
    "Northstar Records",
    "Daybreak Sound",
    "Bluebird Audio",
    "Afterglow Music",
)
PLAYLIST_NAMES = (
    "Demo: Daily Rotation",
    "Demo: New Discoveries",
    "Demo: Late Night Mix",
)


def _image_data_uri(title: str, index: int) -> str:
    initials = escape("".join(word[0] for word in title.split()[:2]).upper())
    color = PALETTE[index % len(PALETTE)]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">'
        f'<rect width="300" height="300" fill="{color}"/>'
        '<circle cx="150" cy="150" r="104" fill="#ffffff" fill-opacity=".12"/>'
        '<text x="150" y="174" text-anchor="middle" fill="#ffffff" '
        'font-family="sans-serif" font-size="76" font-weight="700">'
        f"{initials}</text></svg>"
    )
    return f"data:image/svg+xml,{quote(svg, safe='')}"


def _demo_catalog(year: int) -> dict:
    artists = []
    albums = []
    tracks = []
    track_artists = []
    album_artists = []
    artist_genres = []

    for index, (artist_name, genres) in enumerate(ARTIST_NAMES, start=1):
        artist_uri = f"spotify:artist:demo-{index:02}"
        album_uri = f"spotify:album:demo-{index:02}"
        album_name = (
            f"{artist_name} — "
            f"{('Afterglow', 'Blue Skies', 'Small Hours', 'Home Again')[(index - 1) % 4]}"
        )
        label = LABELS[(index - 1) % len(LABELS)]

        artists.append(
            {
                "uri": artist_uri,
                "name": artist_name,
                "popularity": 88 - index * 4,
                "followers": 180_000 + index * 31_000,
                "image_url": _image_data_uri(artist_name, index),
            }
        )
        albums.append(
            {
                "uri": album_uri,
                "name": album_name,
                "short_name": album_name,
                "album_type": "album",
                "label": label,
                "popularity": 82 - index * 3,
                "total_tracks": 2,
                "release_date": f"{year - ((index - 1) % 6)}-{(index % 12) + 1:02}-01",
                "image_url": _image_data_uri(artist_name, index + 2),
            }
        )
        album_artists.append({"album_uri": album_uri, "artist_uri": artist_uri})
        artist_genres.extend(
            {"artist_uri": artist_uri, "genre": genre} for genre in genres
        )

        for song_index, track_name in enumerate(TRACK_NAMES[index - 1]):
            track_uri = f"spotify:track:demo-{index:02}-{song_index + 1:02}"
            tracks.append(
                {
                    "uri": track_uri,
                    "name": track_name,
                    "short_name": track_name,
                    "popularity": 55 + ((index * 7 + song_index * 11) % 40),
                    "explicit": (index + song_index) % 5 == 0,
                    "duration_ms": 165_000 + index * 4_000 + song_index * 9_000,
                    "album_uri": album_uri,
                    "isrc": None,
                }
            )
            track_artists.append(
                {
                    "track_uri": track_uri,
                    "artist_uri": artist_uri,
                    "artist_index": 0,
                }
            )

    playlists = [
        {
            "uri": f"spotify:playlist:demo-{index:02}",
            "name": name,
            "collaborative": False,
            "public": True,
            "image_url": _image_data_uri(name, index + 3),
            "owner": "spotify-stats-demo",
        }
        for index, name in enumerate(PLAYLIST_NAMES, start=1)
    ]
    playlist_tracks = []
    for index, track in enumerate(tracks):
        playlist_tracks.append(
            {"playlist_uri": playlists[0]["uri"], "track_uri": track["uri"]}
        )
        playlist_tracks.append(
            {
                "playlist_uri": playlists[1 + index % 2]["uri"],
                "track_uri": track["uri"],
            }
        )

    return {
        "artists": artists,
        "albums": albums,
        "tracks": tracks,
        "playlists": playlists,
        "track_artists": track_artists,
        "album_artists": album_artists,
        "artist_genres": artist_genres,
        "playlist_tracks": playlist_tracks,
    }


def _demo_streams(tracks: list[dict], year: int) -> list[tuple]:
    generator = random.Random(year)
    streams = []
    for month in range(1, 13):
        weights = [
            2 + ((month + index * 3) % 8) for index in range(len(tracks))
        ]
        for sample in range(60):
            track = generator.choices(tracks, weights=weights, k=1)[0]
            played_at = datetime(year, month, 1) + timedelta(
                days=(sample * 7) % 28,
                hours=(sample * 5) % 24,
                minutes=(sample * 13) % 60,
                seconds=sample,
            )
            streams.append((track["uri"], played_at))
    return streams


def seed_demo_data(year: int) -> None:
    catalog = _demo_catalog(year)

    with get_connection() as connection:
        cursor = connection.cursor()
        store = SpotifyStore(cursor)
        store.save_artists(catalog["artists"])
        store.save_albums(catalog["albums"])
        store.save_tracks(catalog["tracks"])
        store.save_playlists(catalog["playlists"])
        store.save_track_artists(catalog["track_artists"])
        store.save_album_artists(catalog["album_artists"])
        store.save_artist_genres(catalog["artist_genres"])

        execute_values(
            cursor,
            """
            INSERT INTO playlist_track (playlist_uri, track_uri)
            VALUES %s
            ON CONFLICT (playlist_uri, track_uri) DO NOTHING;
            """,
            [
                (item["playlist_uri"], item["track_uri"])
                for item in catalog["playlist_tracks"]
            ],
        )
        cursor.executemany(
            """
            INSERT INTO liked_track (track_uri) VALUES (%s)
            ON CONFLICT (track_uri) DO NOTHING;
            """,
            [(catalog["tracks"][index]["uri"],) for index in (0, 3, 5, 8, 11, 14)],
        )
        for index, album in enumerate(catalog["albums"]):
            label = LABELS[index % len(LABELS)]
            cursor.execute(
                """
                INSERT INTO record_label (album_uri, standardized_label)
                SELECT %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM record_label
                    WHERE album_uri = %s AND standardized_label = %s
                );
                """,
                (album["uri"], label, album["uri"], label),
            )

        streams = _demo_streams(catalog["tracks"], year)
        execute_values(
            cursor,
            """
            INSERT INTO track_stream (track_uri, played_at)
            VALUES %s
            ON CONFLICT (track_uri, played_at) DO NOTHING;
            """,
            streams,
        )
        connection.commit()

    print(
        f"Seeded demo catalog and {len(streams)} streams for {year}. "
        f"Open http://localhost:5173/?wrapped={year}-01-01..{year + 1}-01-01"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--year",
        type=int,
        default=2025,
        help="calendar year for the sample listening history (default: 2025)",
    )
    parser.add_argument(
        "--allow-database-url",
        action="store_true",
        help="allow DATABASE_URL (use only with a disposable database)",
    )
    args = parser.parse_args()

    if not MIN_YEAR <= args.year <= datetime.now().year:
        parser.error(f"--year must be between {MIN_YEAR} and {datetime.now().year}")
    if postgres_url() and not args.allow_database_url:
        parser.error(
            "DATABASE_URL is set; unset it for local development or pass "
            "--allow-database-url only for a disposable database"
        )

    seed_demo_data(args.year)


if __name__ == "__main__":
    main()
