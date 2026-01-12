WITH month_ends AS (
    SELECT DISTINCT DATE_TRUNC('month', played_at) + INTERVAL '1 month' - INTERVAL '1 second' AS as_of_date
    FROM track_stream
    WHERE track_uri IN :track_uris
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
    WHERE s.track_uri IN :track_uris
        AND s.played_at <= m.as_of_date
    GROUP BY s.track_uri, m.as_of_date
)
SELECT 
    track_uri,
    0 AS track_rank,
    track_stream_count,
    as_of_date
FROM cumulative_counts
ORDER BY track_uri, as_of_date;