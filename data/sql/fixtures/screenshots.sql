\set ON_ERROR_STOP on

BEGIN;

DO $$
BEGIN
    IF current_database() <> 'spotifystats_screenshots' THEN
        RAISE EXCEPTION 'Use only the disposable spotifystats_screenshots database';
    END IF;
END $$;

\ir ../schema.sql

-- The schema is current; replaying historical migrations would recreate old tables.
INSERT INTO version (version)
SELECT 'v025'
WHERE NOT EXISTS (SELECT 1 FROM version);

INSERT INTO artist (uri, name, popularity, followers, image_url)
SELECT
    'spotify:artist:mock' || i,
    (ARRAY['Amber Signals', 'Paper Satellites', 'Velvet Transit',
           'Glass Orchard', 'Quiet Geometry', 'Silver Weather'])[i],
    40 + i * 7,
    10000 * i,
    'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="160" height="160"%3E%3Crect width="160" height="160" fill="%23'
        || (ARRAY['7657a8', '247e91', 'b66c45', '458563', 'a6537e', '5569a8'])[i]
        || '"/%3E%3Ccircle cx="80" cy="80" r="44" fill="white" opacity=".25"/%3E%3C/svg%3E'
FROM generate_series(1, 6) AS i
ON CONFLICT (uri) DO NOTHING;

INSERT INTO album (
    uri, name, short_name, album_type, label, popularity,
    total_tracks, release_date, image_url
)
SELECT
    'spotify:album:mock' || i,
    (ARRAY['Daylight Maps', 'Night Windows', 'Soft Landing', 'Open Water',
           'City Lanterns', 'Slow Motion', 'Green Rooms', 'Distant Gardens',
           'Small Hours', 'Parallel Lines', 'Morning Radio', 'Blue Horizons'])[i],
    '', 'album',
    (ARRAY['Lantern Records', 'Cloudline Music', 'Meadow Sound'])[1 + (i - 1) % 3],
    45 + i * 3, 4,
    (2020 + (i - 1) % 5)::TEXT || '-03-15',
    a.image_url
FROM generate_series(1, 12) AS i
JOIN artist a ON a.uri = 'spotify:artist:mock' || (1 + (i - 1) / 2)
ON CONFLICT (uri) DO NOTHING;

INSERT INTO album_artist (album_uri, artist_uri)
SELECT 'spotify:album:mock' || i, 'spotify:artist:mock' || (1 + (i - 1) / 2)
FROM generate_series(1, 12) AS i
ON CONFLICT DO NOTHING;

INSERT INTO artist_genre (artist_uri, genre)
SELECT
    'spotify:artist:mock' || i,
    (ARRAY['indie pop', 'dream pop', 'alternative rock'])[1 + (i - 1) % 3]
FROM generate_series(1, 6) AS i
ON CONFLICT DO NOTHING;

INSERT INTO record_label (album_uri, standardized_label)
SELECT uri, label FROM album a
WHERE uri LIKE 'spotify:album:mock%'
AND NOT EXISTS (SELECT 1 FROM record_label r WHERE r.album_uri = a.uri);

INSERT INTO track (
    uri, name, short_name, popularity, explicit, duration_ms, album_uri, isrc
)
SELECT
    'spotify:track:mock' || i,
    (ARRAY['First Light', 'Window Seat', 'Long Way Home', 'Afterglow'])[1 + (i - 1) % 4]
        || ' / ' || a.name,
    '', 35 + i % 60, false, 180000 + i * 1000, a.uri, NULL
FROM generate_series(1, 48) AS i
JOIN album a ON a.uri = 'spotify:album:mock' || (1 + (i - 1) / 4)
ON CONFLICT (uri) DO NOTHING;

INSERT INTO track_artist (track_uri, artist_uri, artist_index)
SELECT
    'spotify:track:mock' || i,
    'spotify:artist:mock' || (1 + (i - 1) / 8), 0
FROM generate_series(1, 48) AS i
ON CONFLICT DO NOTHING;

INSERT INTO liked_track (track_uri)
SELECT 'spotify:track:mock' || i FROM generate_series(1, 24) AS i
ON CONFLICT DO NOTHING;

INSERT INTO playlist (uri, name, collaborative, public, owner, image_url)
SELECT
    'spotify:playlist:mock' || i,
    (ARRAY['Morning Rotation', 'Evening Drift', 'Weekend Discoveries'])[i],
    false, true, 'Screenshot Demo',
    (SELECT image_url FROM artist WHERE uri = 'spotify:artist:mock' || i)
FROM generate_series(1, 3) AS i
ON CONFLICT (uri) DO NOTHING;

INSERT INTO playlist_track (playlist_uri, track_uri)
SELECT 'spotify:playlist:mock' || (1 + (i - 1) % 3), 'spotify:track:mock' || i
FROM generate_series(1, 48) AS i
ON CONFLICT DO NOTHING;

INSERT INTO track_stream (track_uri, played_at)
SELECT
    'spotify:track:mock' || track_number,
    TIMESTAMP '2024-01-01 09:00:00'
        + month_number * INTERVAL '1 month'
        + (play_number - 1) * INTERVAL '1 day'
        + track_number * INTERVAL '5 minutes'
FROM generate_series(1, 48) AS track_number
CROSS JOIN generate_series(0, 23) AS month_number
CROSS JOIN generate_series(1, 12) AS play_number
WHERE play_number <= 1 + (track_number * 7 + month_number * 3) % 12
ON CONFLICT DO NOTHING;

INSERT INTO mb_artist (artist_mbid, artist_mb_name, artist_type)
VALUES ('mock-producer-1', 'Rowan Echo', 'Person'),
       ('mock-producer-2', 'River Vale', 'Person')
ON CONFLICT (artist_mbid) DO NOTHING;

INSERT INTO mb_recording (recording_mbid, recording_title)
SELECT 'mock-recording-' || i, name
FROM generate_series(1, 48) AS i
JOIN track ON uri = 'spotify:track:mock' || i
ON CONFLICT (recording_mbid) DO NOTHING;

INSERT INTO sp_track_mb_recording (spotify_track_uri, recording_mbid)
SELECT 'spotify:track:mock' || i, 'mock-recording-' || i
FROM generate_series(1, 48) AS i
ON CONFLICT DO NOTHING;

INSERT INTO mb_recording_credit (recording_mbid, artist_mbid, raw_role, credit_type)
SELECT
    'mock-recording-' || i,
    'mock-producer-' || (1 + i % 2),
    'producer', 'producer'
FROM generate_series(1, 48) AS i
ON CONFLICT DO NOTHING;

COMMIT;

SELECT
    (SELECT COUNT(*) FROM artist) AS artists,
    (SELECT COUNT(*) FROM album) AS albums,
    (SELECT COUNT(*) FROM track) AS tracks,
    (SELECT COUNT(*) FROM track_stream) AS streams;
