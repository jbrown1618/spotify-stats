SELECT 
    track_uri,
    COUNT(*) AS track_stream_count,
    ROW_NUMBER() OVER(ORDER BY COUNT(*) DESC, track_uri) AS track_rank
FROM track_stream
WHERE
    played_at >= :min_stream_date 
    AND played_at < :max_stream_date
GROUP BY track_uri
ORDER BY COUNT(*) DESC, track_uri
LIMIT 100;