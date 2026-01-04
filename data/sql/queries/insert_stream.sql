INSERT INTO stream (track_uri, played_at)
VALUES (%(track_uri)s, TO_TIMESTAMP(%(played_at)s))
ON CONFLICT (track_uri, played_at) DO NOTHING;
