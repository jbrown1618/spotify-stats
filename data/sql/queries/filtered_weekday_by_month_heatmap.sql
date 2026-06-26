SELECT
    TO_CHAR(DATE_TRUNC('month', s.played_at)::DATE, 'YYYY-MM') AS month,
    EXTRACT(ISODOW FROM s.played_at)::INT AS day_of_week,
    COUNT(*)::INT AS stream_count
FROM matching_track_uris m
    INNER JOIN track_stream s ON s.track_uri = m.track_uri
WHERE
    (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
    AND
    (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
GROUP BY month, day_of_week
ORDER BY month, day_of_week;
