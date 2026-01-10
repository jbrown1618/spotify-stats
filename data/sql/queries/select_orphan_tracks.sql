SELECT DISTINCT s.track_uri, t.name
FROM track_stream s
INNER JOIN track t ON t.uri = s.track_uri
WHERE s.track_uri NOT IN (
    SELECT pt.track_uri FROM playlist_track pt
)