SELECT
    EXTRACT(YEAR FROM s.played_at)::INT AS year,
    EXTRACT(MONTH FROM s.played_at)::INT AS month,
    COUNT(*)::INT AS stream_count
FROM matching_track_uris m
    INNER JOIN track_stream s ON s.track_uri = m.track_uri
WHERE
    (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
    AND
    (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
GROUP BY year, month
ORDER BY year, month;
