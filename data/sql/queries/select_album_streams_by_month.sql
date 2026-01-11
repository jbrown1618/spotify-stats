SELECT 
    t.album_uri,
    EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
    EXTRACT(MONTH FROM s.played_at)::INTEGER AS month,
    COUNT(*) AS stream_count
FROM track_stream s
INNER JOIN track t ON t.uri = s.track_uri
WHERE t.album_uri IN %(album_uris)s
    AND (%(from_date)s IS NULL OR s.played_at >= %(from_date)s)
    AND (%(to_date)s IS NULL OR s.played_at <= %(to_date)s)
GROUP BY t.album_uri, year, month;