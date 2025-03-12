INSERT INTO listening_history (listening_period_id, track_uri, stream_count)
VALUES (%(period_id)s, %(track_uri)s, %(stream_count)s)
ON CONFLICT (listening_period_id, track_uri) DO UPDATE
SET stream_count = listening_history.stream_count + %(stream_count)s;