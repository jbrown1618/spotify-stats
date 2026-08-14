SELECT
    id,
    type,
    arguments
FROM job
WHERE status = %(status)s
ORDER BY queue_time ASC
LIMIT 1;
