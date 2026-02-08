-- Find tracks that have streams but are not in any playlist
SELECT DISTINCT ts.track_uri, t.name
FROM track_stream ts
INNER JOIN track t ON t.uri = ts.track_uri
LEFT JOIN playlist_track pt ON pt.track_uri = ts.track_uri
WHERE pt.track_uri IS NULL