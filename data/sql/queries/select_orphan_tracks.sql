SELECT DISTINCT track_uri, name
FROM (
    -- Orphans from track_stream
    SELECT s.track_uri, t.name
    FROM track_stream s
    INNER JOIN track t ON t.uri = s.track_uri
    WHERE s.track_uri NOT IN (
        SELECT pt.track_uri FROM playlist_track pt
    )
    UNION
    -- Orphans from listening_history
    SELECT h.track_uri, t.name
    FROM listening_history h
    INNER JOIN track t ON t.uri = h.track_uri
    WHERE h.track_uri NOT IN (
        SELECT pt.track_uri FROM playlist_track pt
    )
) AS orphans