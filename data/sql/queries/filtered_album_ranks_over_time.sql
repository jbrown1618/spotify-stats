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
),
month_ends AS (
    SELECT DISTINCT DATE_TRUNC('month', s.played_at) + INTERVAL '1 month' - INTERVAL '1 second' AS as_of_date
    FROM track_stream s
    INNER JOIN track t ON t.uri = s.track_uri
    WHERE t.album_uri IN (SELECT album_uri FROM top_albums)
        AND (:from_date IS NULL OR s.played_at >= :from_date)
        AND (:to_date IS NULL OR s.played_at <= :to_date)
),
cumulative_counts AS (
    SELECT 
        t.album_uri,
        m.as_of_date,
        COUNT(*) AS album_stream_count
    FROM track_stream s
    INNER JOIN track t ON t.uri = s.track_uri
    CROSS JOIN month_ends m
    WHERE t.album_uri IN (SELECT album_uri FROM top_albums)
        AND s.played_at <= m.as_of_date
    GROUP BY t.album_uri, m.as_of_date
)
SELECT 
    cc.album_uri,
    0 AS album_rank,
    cc.album_stream_count,
    cc.as_of_date,
    al.short_name AS album_short_name,
    al.name AS album_name,
    al.image_url AS album_image_url
FROM cumulative_counts cc
INNER JOIN album al ON al.uri = cc.album_uri
ORDER BY cc.album_uri, cc.as_of_date;
