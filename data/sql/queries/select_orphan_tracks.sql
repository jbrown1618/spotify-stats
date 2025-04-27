SELECT DISTINCT tt.track_uri, t.name
FROM top_track tt
INNER JOIN track t ON t.uri = tt.track_uri
WHERE tt.track_uri NOT IN (
    SELECT pt.track_uri FROM playlist_track pt
)
UNION ALL (
    SELECT DISTINCT h.track_uri, t.name
    FROM listening_history h
    INNER JOIN track t ON t.uri = h.track_uri
    WHERE h.track_uri NOT IN (
        SELECT pt.track_uri FROM playlist_track pt
    )
);