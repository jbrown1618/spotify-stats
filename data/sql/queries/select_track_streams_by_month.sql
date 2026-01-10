SELECT 
    s.track_uri,
    EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
    EXTRACT(MONTH FROM s.played_at)::INTEGER AS month,
    COUNT(*) AS stream_count
FROM track_stream s
WHERE s.track_uri IN %(track_uris)s
    AND (%(from_date)s IS NULL OR s.played_at >= %(from_date)s)
    AND (%(to_date)s IS NULL OR s.played_at <= %(to_date)s)
GROUP BY s.track_uri, year, month;