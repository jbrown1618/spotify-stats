-- Find liked tracks matching the current filter whose total stream counts fall within
-- a given percentile range (e.g. low_percentile=0.5, high_percentile=0.7 for the
-- 50th-70th percentile), sorted with least-recently-streamed first.
-- Parameters: low_percentile (0.0 to 1.0), high_percentile (0.0 to 1.0), filter_tracks (boolean)
WITH track_stats AS (
    SELECT
        s.track_uri,
        COUNT(*) AS total_streams,
        MAX(s.played_at) AS last_played
    FROM track_stream s
    WHERE (:filter_tracks = FALSE OR s.track_uri IN (SELECT track_uri FROM matching_track_uris))
      AND s.track_uri IN (SELECT track_uri FROM liked_track)
    GROUP BY s.track_uri
),
stream_percentiles AS (
    SELECT
        PERCENTILE_CONT(:low_percentile) WITHIN GROUP (ORDER BY total_streams) AS low_streams,
        PERCENTILE_CONT(:high_percentile) WITHIN GROUP (ORDER BY total_streams) AS high_streams
    FROM track_stats
)
SELECT
    ts.track_uri,
    ts.total_streams,
    ts.last_played
FROM track_stats ts
CROSS JOIN stream_percentiles sp
WHERE ts.total_streams >= sp.low_streams
  AND ts.total_streams <= sp.high_streams
ORDER BY ts.last_played ASC;
