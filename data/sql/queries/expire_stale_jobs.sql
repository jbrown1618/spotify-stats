UPDATE job
SET
    status = %(failure_status)s,
    error = 'Job expired after remaining in progress for more than one hour',
    end_time = CURRENT_TIMESTAMP
WHERE status = %(in_progress_status)s
    AND start_time < CURRENT_TIMESTAMP - INTERVAL '1 hour';
