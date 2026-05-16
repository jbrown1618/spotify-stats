WITH top_albums AS (
    SELECT t.album_uri, COUNT(*) AS total_streams
    FROM track_stream s
    INNER JOIN track t ON t.uri = s.track_uri
    WHERE s.track_uri IN (SELECT track_uri FROM matching_track_uris)
        AND (:from_date IS NULL OR s.played_at >= :from_date)
        AND (:to_date IS NULL OR s.played_at <= :to_date)
    GROUP BY t.album_uri
    ORDER BY total_streams DESC
    LIMIT :n
)
SELECT 
    t.album_uri,
    EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
    EXTRACT(MONTH FROM s.played_at)::INTEGER AS month,
    COUNT(*) AS stream_count,
    al.short_name AS album_short_name,
    al.name AS album_name,
    al.image_url AS album_image_url
FROM track_stream s
INNER JOIN track t ON t.uri = s.track_uri
INNER JOIN album al ON al.uri = t.album_uri
WHERE t.album_uri IN (SELECT album_uri FROM top_albums)
    AND (:from_date IS NULL OR s.played_at >= :from_date)
    AND (:to_date IS NULL OR s.played_at <= :to_date)
GROUP BY t.album_uri, year, month, al.short_name, al.name, al.image_url;
