SELECT DISTINCT to_time
FROM listening_period
WHERE to_time NOT IN (
    SELECT DISTINCT as_of_date FROM track_rank
);