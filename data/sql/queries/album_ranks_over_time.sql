WITH month_ends AS (
    SELECT DISTINCT DATE_TRUNC('month', s.played_at) + INTERVAL '1 month' - INTERVAL '1 second' AS as_of_date
    FROM track_stream s
    INNER JOIN track t ON t.uri = s.track_uri
    WHERE t.album_uri IN :album_uris
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
    WHERE t.album_uri IN :album_uris
        AND s.played_at <= m.as_of_date
    GROUP BY t.album_uri, m.as_of_date
)
SELECT 
    album_uri,
    0 AS album_rank,
    album_stream_count,
    as_of_date
FROM cumulative_counts
ORDER BY album_uri, as_of_date;