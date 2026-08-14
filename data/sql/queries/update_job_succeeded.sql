UPDATE job
SET
    status = %(status)s,
    end_time = CURRENT_TIMESTAMP
WHERE id = %(id)s;
