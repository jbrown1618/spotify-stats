SELECT 
    s.track_uri,
    EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
    EXTRACT(MONTH FROM s.played_at)::INTEGER AS month,
    COUNT(*) AS stream_count,
    t.short_name AS track_short_name,
    t.name AS track_name,
    al.image_url AS album_image_url
FROM track_stream s
INNER JOIN track t ON t.uri = s.track_uri
INNER JOIN album al ON al.uri = t.album_uri
WHERE s.track_uri IN %(track_uris)s
    AND (%(from_date)s IS NULL OR s.played_at >= %(from_date)s)
    AND (%(to_date)s IS NULL OR s.played_at <= %(to_date)s)
GROUP BY s.track_uri, year, month, t.short_name, t.name, al.image_url;