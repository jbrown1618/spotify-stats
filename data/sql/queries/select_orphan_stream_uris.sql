SELECT DISTINCT ts.track_uri
FROM track_stream ts
LEFT JOIN playlist_track pt ON pt.track_uri = ts.track_uri
WHERE pt.track_uri IS NULL;
