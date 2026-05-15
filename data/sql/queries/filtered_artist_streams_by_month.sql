WITH top_artists AS (
    SELECT ta.artist_uri, COUNT(*) AS total_streams
    FROM track_stream s
    INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
    WHERE s.track_uri IN (SELECT track_uri FROM matching_track_uris)
        AND (:from_date IS NULL OR s.played_at >= :from_date)
        AND (:to_date IS NULL OR s.played_at <= :to_date)
    GROUP BY ta.artist_uri
    ORDER BY total_streams DESC
    LIMIT :n
)
SELECT 
    ta.artist_uri,
    EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
    EXTRACT(MONTH FROM s.played_at)::INTEGER AS month,
    COUNT(*) AS stream_count
FROM track_stream s
INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
WHERE ta.artist_uri IN (SELECT artist_uri FROM top_artists)
    AND (:from_date IS NULL OR s.played_at >= :from_date)
    AND (:to_date IS NULL OR s.played_at <= :to_date)
GROUP BY ta.artist_uri, year, month;
