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
    (
        SELECT COUNT(uri) 
        FROM (
            SELECT DISTINCT it.uri
            FROM track it 
            INNER JOIN liked_track ilt ON ilt.track_uri = it.uri
            WHERE it.album_uri = al.uri
            AND (:filter_tracks = FALSE OR it.uri IN :track_uris)
        )
    ) AS album_liked_track_count,
    (
        SELECT COUNT(uri) 
        FROM (
            SELECT DISTINCT it.uri
            FROM track it 
            WHERE it.album_uri = al.uri
            AND (:filter_tracks = FALSE OR it.uri IN :track_uris)
        )
    ) AS album_track_count,
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
WHERE (:filter_tracks = FALSE OR t.uri IN :track_uris)
GROUP BY 
    al.uri,
    al.name,
    al.short_name,
    al.album_type,
    al.label,
    al.popularity,
    al.release_date,
    al.image_url,
    sc.stream_count

ORDER BY sc.stream_count DESC NULLS LAST;