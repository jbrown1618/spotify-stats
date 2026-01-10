SELECT 
    ta.artist_uri,
    EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
    EXTRACT(MONTH FROM s.played_at)::INTEGER AS month,
    COUNT(*) AS stream_count
FROM track_stream s
INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
WHERE ta.artist_uri IN %(artist_uris)s
    AND (%(from_date)s IS NULL OR s.played_at >= %(from_date)s)
    AND (%(to_date)s IS NULL OR s.played_at <= %(to_date)s)
GROUP BY ta.artist_uri, year, month;