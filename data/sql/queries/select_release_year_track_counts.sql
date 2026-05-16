DROP TABLE IF EXISTS tmp_release_year_track_counts;

CREATE TEMPORARY TABLE tmp_release_year_track_counts AS
SELECT
    (CASE
        WHEN LENGTH(al.release_date) = 10 THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM-DD'))
        WHEN LENGTH(al.release_date) = 7 THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM'))
        WHEN LENGTH(al.release_date) = 4 THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY'))
        ELSE 0
    END) AS album_release_year,
    COUNT(DISTINCT t.uri) AS total_track_count,
    COUNT(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN t.uri END) AS total_liked_track_count
FROM track t
    INNER JOIN album al ON al.uri = t.album_uri
    LEFT JOIN liked_track lt ON lt.track_uri = t.uri
GROUP BY album_release_year;

SELECT 
    i.album_release_year as release_year,
    COUNT(i.track_uri) as track_count,
    COUNT(i.track_liked) AS liked_track_count,
    COALESCE(rytc.total_track_count, 0) as total_track_count,
    COALESCE(rytc.total_liked_track_count, 0) as total_liked_track_count
FROM (
    SELECT 
        it.uri as track_uri,
        ilt.track_uri AS track_liked,
        (
            case
            when length(ial.release_date) = 10
                then extract(year from to_date(ial.release_date, 'YYYY-MM-DD'))
            when length(ial.release_date) = 7
                then extract(year from to_date(ial.release_date, 'YYYY-MM'))
            when length(ial.release_date) = 4
                then extract(year from to_date(ial.release_date, 'YYYY'))
            else 0
            end
        ) as album_release_year
    FROM album ial
    INNER JOIN track it ON it.album_uri = ial.uri
    LEFT JOIN liked_track ilt ON ilt.track_uri = it.uri
    WHERE it.uri IN (SELECT track_uri FROM matching_track_uris)
) i
LEFT JOIN tmp_release_year_track_counts rytc ON rytc.album_release_year = i.album_release_year
GROUP BY i.album_release_year, rytc.total_track_count, rytc.total_liked_track_count
