UPDATE job
SET
    status = %(status)s,
    start_time = CURRENT_TIMESTAMP
WHERE id = %(id)s;
