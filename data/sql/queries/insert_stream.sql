INSERT INTO track_stream (track_uri, played_at)
VALUES (:track_uri, TO_TIMESTAMP(:played_at))
ON CONFLICT (track_uri, played_at) DO NOTHING;
