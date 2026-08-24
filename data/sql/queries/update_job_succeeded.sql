UPDATE job
SET
    status = %(status)s,
    summary = CAST(%(summary)s AS JSONB),
    end_time = CURRENT_TIMESTAMP
WHERE id = %(id)s;
