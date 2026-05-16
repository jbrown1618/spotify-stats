WITH top_tracks AS (
    SELECT s.track_uri, COUNT(*) AS total_streams
    FROM track_stream s
    WHERE s.track_uri IN (SELECT track_uri FROM matching_track_uris)
        AND (:from_date IS NULL OR s.played_at >= :from_date)
        AND (:to_date IS NULL OR s.played_at <= :to_date)
    GROUP BY s.track_uri
    ORDER BY total_streams DESC
    LIMIT :n
),
month_ends AS (
    SELECT DISTINCT DATE_TRUNC('month', played_at) + INTERVAL '1 month' - INTERVAL '1 second' AS as_of_date
    FROM track_stream
    WHERE track_uri IN (SELECT track_uri FROM top_tracks)
        AND (:from_date IS NULL OR played_at >= :from_date)
        AND (:to_date IS NULL OR played_at <= :to_date)
),
cumulative_counts AS (
    SELECT 
        s.track_uri,
        m.as_of_date,
        COUNT(*) AS track_stream_count
    FROM track_stream s
    CROSS JOIN month_ends m
    WHERE s.track_uri IN (SELECT track_uri FROM top_tracks)
        AND s.played_at <= m.as_of_date
    GROUP BY s.track_uri, m.as_of_date
)
SELECT 
    cc.track_uri,
    0 AS track_rank,
    cc.track_stream_count,
    cc.as_of_date,
    t.short_name AS track_short_name,
    t.name AS track_name,
    al.image_url AS album_image_url
FROM cumulative_counts cc
INNER JOIN track t ON t.uri = cc.track_uri
INNER JOIN album al ON al.uri = t.album_uri
ORDER BY cc.track_uri, cc.as_of_date;
