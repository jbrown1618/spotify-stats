WITH track_stats AS (
    SELECT
        mt.track_uri,
        COUNT(*) AS total_streams
    FROM matching_track_uris mt
    INNER JOIN liked_track lt ON lt.track_uri = mt.track_uri
    INNER JOIN track_stream s ON s.track_uri = mt.track_uri
    WHERE
        (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
        AND
        (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
    GROUP BY mt.track_uri
),
track_recency AS (
    SELECT
        s.track_uri,
        MAX(s.played_at) AS last_played
    FROM track_stream s
    GROUP BY s.track_uri
),
stream_percentiles AS (
    SELECT
        PERCENTILE_CONT(:percentile_min) WITHIN GROUP (ORDER BY total_streams) AS min_streams,
        PERCENTILE_CONT(:percentile_max) WITHIN GROUP (ORDER BY total_streams) AS max_streams
    FROM track_stats
)
SELECT
    ts.track_uri,
    ts.total_streams,
    tr.last_played
FROM track_stats ts
INNER JOIN track_recency tr ON tr.track_uri = ts.track_uri
CROSS JOIN stream_percentiles sp
WHERE
    ts.total_streams >= sp.min_streams
    AND
    ts.total_streams <= sp.max_streams
ORDER BY tr.last_played ASC, ts.track_uri ASC
LIMIT :limit;
