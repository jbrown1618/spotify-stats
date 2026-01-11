-- Find artists with significant listening history that haven't been played recently
-- Parameters: :percentile (0.0 to 1.0), :filter_tracks (boolean), :track_uris (array)
WITH artist_stats AS (
    SELECT 
        ta.artist_uri,
        COUNT(*) AS total_streams,
        MAX(s.played_at) AS last_played
    FROM track_stream s
    INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
    WHERE (:filter_tracks = FALSE OR s.track_uri IN :track_uris)
    GROUP BY ta.artist_uri
),
stream_percentiles AS (
    SELECT 
        PERCENTILE_CONT(:percentile) WITHIN GROUP (ORDER BY total_streams) AS percentile_streams
    FROM artist_stats
)
SELECT 
    ast.artist_uri,
    ast.total_streams,
    ast.last_played
FROM artist_stats ast
CROSS JOIN stream_percentiles sp
WHERE ast.total_streams >= sp.percentile_streams
  AND ast.last_played < NOW() - INTERVAL '2 months'
ORDER BY ast.last_played ASC
LIMIT 20;
