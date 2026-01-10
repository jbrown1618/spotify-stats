SELECT DISTINCT DATE_TRUNC('month', played_at) + INTERVAL '1 month' - INTERVAL '1 second' AS to_time
FROM track_stream
WHERE DATE_TRUNC('month', played_at) + INTERVAL '1 month' - INTERVAL '1 second' NOT IN (
    SELECT DISTINCT as_of_date FROM track_rank
);