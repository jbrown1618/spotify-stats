SELECT 
    s.track_uri,
    EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
    EXTRACT(MONTH FROM s.played_at)::INTEGER AS month,
    COUNT(*) AS stream_count
FROM track_stream s
WHERE s.track_uri IN :track_uris
    AND (:from_date IS NULL OR s.played_at >= :from_date)
    AND (:to_date IS NULL OR s.played_at <= :to_date)
GROUP BY s.track_uri, year, month;