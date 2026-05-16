WITH top_tracks AS (
    SELECT s.track_uri, COUNT(*) AS total_streams
    FROM track_stream s
    WHERE s.track_uri IN (SELECT track_uri FROM matching_track_uris)
        AND (:from_date IS NULL OR s.played_at >= :from_date)
        AND (:to_date IS NULL OR s.played_at <= :to_date)
    GROUP BY s.track_uri
    ORDER BY total_streams DESC
    LIMIT :n
)
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
WHERE s.track_uri IN (SELECT track_uri FROM top_tracks)
    AND (:from_date IS NULL OR s.played_at >= :from_date)
    AND (:to_date IS NULL OR s.played_at <= :to_date)
GROUP BY s.track_uri, year, month, t.short_name, t.name, al.image_url;
