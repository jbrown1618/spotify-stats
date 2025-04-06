SELECT 
    track_uri,
    SUM(h.stream_count) AS track_stream_count,
    ROW_NUMBER() OVER(ORDER BY SUM(h.stream_count) DESC, track_uri) AS track_rank
FROM listening_period p
    INNER JOIN listening_history h ON p.id = h.listening_period_id
WHERE
    p.from_time >= :min_stream_date 
    AND p.to_time < :max_stream_date
    AND h.track_uri in :track_uris
GROUP BY h.track_uri
ORDER BY SUM(h.stream_count) DESC, track_uri;