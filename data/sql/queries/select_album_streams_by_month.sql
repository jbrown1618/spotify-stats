SELECT 
    album_uri,
    year,
    month,
    SUM(stream_count) AS stream_count
FROM (
    SELECT 
        t.album_uri,
        EXTRACT(YEAR FROM p.from_time) AS year,
        EXTRACT(MONTH FROM p.to_time) AS month,
        h.stream_count
    FROM listening_history h
        INNER JOIN listening_period p ON p.id = h.listening_period_id
        INNER JOIN track t ON t.uri = h.track_uri
    WHERE t.album_uri IN %(album_uris)s
)
GROUP BY album_uri, year, month;