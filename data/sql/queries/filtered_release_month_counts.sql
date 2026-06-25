SELECT
    (
        CASE
        WHEN LENGTH(al.release_date) = 10
            THEN EXTRACT(MONTH FROM TO_DATE(al.release_date, 'YYYY-MM-DD'))
        WHEN LENGTH(al.release_date) = 7
            THEN EXTRACT(MONTH FROM TO_DATE(al.release_date, 'YYYY-MM'))
        END
    )::INT AS release_month,
    COUNT(DISTINCT t.uri)::INT AS track_count,
    COUNT(DISTINCT lt.track_uri)::INT AS liked_track_count
FROM matching_track_uris m
    INNER JOIN track t ON t.uri = m.track_uri
    INNER JOIN album al ON al.uri = t.album_uri
    LEFT JOIN liked_track lt ON lt.track_uri = t.uri
WHERE LENGTH(al.release_date) IN (7, 10)
GROUP BY release_month
ORDER BY release_month;
