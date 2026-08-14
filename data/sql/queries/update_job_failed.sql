UPDATE job
SET
    status = %(status)s,
    error = %(error)s,
    end_time = CURRENT_TIMESTAMP
WHERE id = %(id)s;
