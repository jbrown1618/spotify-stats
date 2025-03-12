UPDATE listening_period
SET to_time = TO_TIMESTAMP(%(tt)s)
WHERE id = %(period_id)s