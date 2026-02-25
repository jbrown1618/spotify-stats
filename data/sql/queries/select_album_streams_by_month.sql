SELECT 
    t.album_uri,
    EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
    EXTRACT(MONTH FROM s.played_at)::INTEGER AS month,
    COUNT(*) AS stream_count
FROM track_stream s
INNER JOIN track t ON t.uri = s.track_uri
WHERE t.album_uri IN :album_uris
    AND (:from_date IS NULL OR s.played_at >= :from_date)
    AND (:to_date IS NULL OR s.played_at <= :to_date)
GROUP BY t.album_uri, year, month;