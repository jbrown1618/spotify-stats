WITH month_ends AS (
    SELECT DISTINCT DATE_TRUNC('month', s.played_at) + INTERVAL '1 month' - INTERVAL '1 second' AS as_of_date
    FROM track_stream s
    INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
    WHERE ta.artist_uri IN :artist_uris
        AND (:from_date IS NULL OR s.played_at >= :from_date)
        AND (:to_date IS NULL OR s.played_at <= :to_date)
),
cumulative_counts AS (
    SELECT 
        ta.artist_uri,
        m.as_of_date,
        COUNT(*) AS artist_stream_count
    FROM track_stream s
    INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
    CROSS JOIN month_ends m
    WHERE ta.artist_uri IN :artist_uris
        AND s.played_at <= m.as_of_date
    GROUP BY ta.artist_uri, m.as_of_date
)
SELECT 
    artist_uri,
    0 AS artist_rank,
    artist_stream_count,
    as_of_date
FROM cumulative_counts
ORDER BY artist_uri, as_of_date;