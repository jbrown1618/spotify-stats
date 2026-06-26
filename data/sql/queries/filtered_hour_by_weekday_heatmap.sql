SELECT
    EXTRACT(ISODOW FROM s.played_at)::INT AS day_of_week,
    EXTRACT(HOUR FROM s.played_at)::INT AS hour,
    COUNT(*)::INT AS stream_count
FROM matching_track_uris m
    INNER JOIN track_stream s ON s.track_uri = m.track_uri
WHERE
    (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
    AND
    (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
GROUP BY day_of_week, hour
ORDER BY day_of_week, hour;
