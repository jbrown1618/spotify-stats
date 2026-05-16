DROP TABLE IF EXISTS tmp_album_stream_counts;

CREATE TEMPORARY TABLE tmp_album_stream_counts AS
SELECT t.album_uri, COUNT(*) AS stream_count
FROM track_stream s
INNER JOIN track t
    ON t.uri = s.track_uri
WHERE 
    (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
    AND 
    (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
GROUP BY t.album_uri;

DROP TABLE IF EXISTS tmp_album_track_counts;

CREATE TEMPORARY TABLE tmp_album_track_counts AS
SELECT
    t.album_uri,
    COUNT(DISTINCT t.uri) AS track_count,
    COUNT(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN t.uri END) AS liked_track_count
FROM track t
    INNER JOIN matching_track_uris m ON m.track_uri = t.uri
    LEFT JOIN liked_track lt ON lt.track_uri = t.uri
GROUP BY t.album_uri;

SELECT 
    al.uri AS album_uri,
    al.name AS album_name,
    al.short_name AS album_short_name,
    al.album_type,
    al.label AS album_label,
    al.popularity AS album_popularity,
    al.release_date AS album_release_date,
    al.image_url AS album_image_url,
    sc.stream_count AS album_stream_count,
    COALESCE(tc.liked_track_count, 0) AS album_liked_track_count,
    COALESCE(tc.track_count, 0) AS album_track_count,
    (
        CASE
        WHEN LENGTH(al.release_date) = 10
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM-DD'))
        WHEN LENGTH(al.release_date) = 7
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM'))
        WHEN LENGTH(al.release_date) = 4
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY'))
        ELSE 0
        END
    ) AS album_release_year
FROM album al
    INNER JOIN track t ON t.album_uri = al.uri
    LEFT JOIN tmp_album_stream_counts sc ON sc.album_uri = al.uri
    LEFT JOIN tmp_album_track_counts tc ON tc.album_uri = al.uri
WHERE t.uri IN (SELECT track_uri FROM matching_track_uris)
GROUP BY 
    al.uri,
    al.name,
    al.short_name,
    al.album_type,
    al.label,
    al.popularity,
    al.release_date,
    al.image_url,
    sc.stream_count,
    tc.liked_track_count,
    tc.track_count

ORDER BY sc.stream_count DESC NULLS LAST;