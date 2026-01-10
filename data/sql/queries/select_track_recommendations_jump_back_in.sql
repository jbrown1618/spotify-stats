-- Find liked tracks with significant listening history that haven't been played recently
-- Uses percentile to find tracks with above-average play counts
-- Parameters: :percentile (0.0 to 1.0), :filter_tracks (boolean), :track_uris (array)
WITH track_stats AS (
    SELECT 
        s.track_uri,
        COUNT(*) AS total_streams,
        MAX(s.played_at) AS last_played
    FROM track_stream s
    INNER JOIN liked_track lt ON lt.track_uri = s.track_uri
    WHERE (:filter_tracks = FALSE OR s.track_uri IN :track_uris)
    GROUP BY s.track_uri
),
stream_percentiles AS (
    SELECT 
        PERCENTILE_CONT(:percentile) WITHIN GROUP (ORDER BY total_streams) AS percentile_streams
    FROM track_stats
)
SELECT 
    ts.track_uri,
    ts.total_streams,
    ts.last_played
FROM track_stats ts
CROSS JOIN stream_percentiles sp
WHERE ts.total_streams >= sp.percentile_streams
  AND ts.last_played < NOW() - INTERVAL '2 months'
ORDER BY ts.last_played ASC
LIMIT 20;
