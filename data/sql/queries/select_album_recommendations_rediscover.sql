-- Find albums with significant listening history that haven't been played recently
-- Only considers albums with at least 2 tracks with listens
-- Parameters: :percentile (0.0 to 1.0), :filter_tracks (boolean), :track_uris (array)
WITH album_stats AS (
    SELECT 
        t.album_uri,
        COUNT(*) AS total_streams,
        COUNT(DISTINCT s.track_uri) AS tracks_with_listens,
        MAX(s.played_at) AS last_played
    FROM track_stream s
    INNER JOIN track t ON t.uri = s.track_uri
    WHERE (:filter_tracks = FALSE OR s.track_uri IN :track_uris)
    GROUP BY t.album_uri
    HAVING COUNT(DISTINCT s.track_uri) >= 2
),
stream_percentiles AS (
    SELECT 
        PERCENTILE_CONT(:percentile) WITHIN GROUP (ORDER BY total_streams) AS percentile_streams
    FROM album_stats
)
SELECT 
    als.album_uri,
    als.total_streams,
    als.last_played
FROM album_stats als
CROSS JOIN stream_percentiles sp
WHERE als.total_streams >= sp.percentile_streams
  AND als.last_played < NOW() - INTERVAL '2 months'
ORDER BY als.last_played ASC
LIMIT 20;
