SELECT id, from_time, to_time
FROM listening_period
WHERE to_time = (
    SELECT MAX(to_time) from listening_period
)
LIMIT 1;