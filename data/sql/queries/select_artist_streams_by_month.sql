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
        AND (%(from_date)s IS NULL OR p.from_time >= %(from_date)s)
        AND (%(to_date)s IS NULL OR p.to_time <= %(to_date)s)
)
GROUP BY artist_uri, year, month;