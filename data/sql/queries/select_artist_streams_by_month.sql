SELECT 
    artist_uri,
    year,
    month,
    SUM(stream_count) AS stream_count
FROM (
    SELECT 
        ta.artist_uri,
        EXTRACT(YEAR FROM p.from_time) AS year,
        EXTRACT(MONTH FROM p.to_time) AS month,
        h.stream_count
    FROM listening_history h
        INNER JOIN listening_period p ON p.id = h.listening_period_id
        INNER JOIN track_artist ta ON ta.track_uri = h.track_uri
    WHERE ta.artist_uri IN %(artist_uris)s
)
GROUP BY artist_uri, year, month;