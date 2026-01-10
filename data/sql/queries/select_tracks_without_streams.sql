SELECT track_uri
FROM track_stream
WHERE track_uri NOT IN (
    SELECT uri FROM track
);