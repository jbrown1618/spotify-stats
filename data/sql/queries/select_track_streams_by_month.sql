SELECT 
    track_uri,
    year,
    month,
    SUM(stream_count) AS stream_count
FROM (
    SELECT 
        h.track_uri,
        EXTRACT(YEAR FROM p.from_time) AS year,
        EXTRACT(MONTH FROM p.to_time) AS month,
        h.stream_count
    FROM listening_history h
        INNER JOIN listening_period p ON p.id = h.listening_period_id
    WHERE h.track_uri IN %(track_uris)s
)
GROUP BY track_uri, year, month;