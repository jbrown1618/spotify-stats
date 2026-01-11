SELECT 
    EXTRACT(YEAR FROM played_at)::INTEGER AS year,
    EXTRACT(MONTH FROM played_at)::INTEGER AS month,
    COUNT(*) AS stream_count
FROM track_stream
WHERE track_uri IN %(track_uris)s
GROUP BY year, month;