WITH track_first_streams AS (
    SELECT
        s.track_uri,
        MIN(s.played_at) AS first_played_at
    FROM matching_track_uris m
        INNER JOIN track_stream s ON s.track_uri = m.track_uri
    GROUP BY s.track_uri
),
track_discovery AS (
    SELECT
        tfs.track_uri,
        tfs.first_played_at,
        COUNT(*) FILTER (WHERE s.played_at > tfs.first_played_at)::INT AS subsequent_stream_count
    FROM track_first_streams tfs
        INNER JOIN track_stream s ON s.track_uri = tfs.track_uri
    GROUP BY tfs.track_uri, tfs.first_played_at
)
SELECT
    TO_CHAR(DATE_TRUNC('month', first_played_at), 'YYYY-MM') AS month,
    COUNT(*)::INT AS first_stream_count,
    COUNT(*) FILTER (WHERE subsequent_stream_count > 0)::INT AS retained_track_count
FROM track_discovery
WHERE
    (:wrapped_start_date IS NULL OR :wrapped_start_date <= first_played_at)
    AND
    (:wrapped_end_date IS NULL OR :wrapped_end_date >= first_played_at)
GROUP BY month
ORDER BY month;
