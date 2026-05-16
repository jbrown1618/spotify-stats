DROP TABLE IF EXISTS tmp_label_track_counts;

CREATE TEMPORARY TABLE tmp_label_track_counts AS
SELECT
    rl.standardized_label,
    COUNT(DISTINCT t.uri) AS total_track_count,
    COUNT(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN t.uri END) AS total_liked_track_count
FROM record_label rl
    INNER JOIN track t ON t.album_uri = rl.album_uri
    LEFT JOIN liked_track lt ON lt.track_uri = t.uri
GROUP BY rl.standardized_label;

SELECT
    rl.standardized_label as label, 
    count(DISTINCT t.uri) as label_track_count,
    COALESCE(ltc.total_track_count, 0) as label_total_track_count,
    count(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN t.uri END) as label_liked_track_count,
    COALESCE(ltc.total_liked_track_count, 0) as label_total_liked_track_count
FROM record_label rl
    INNER JOIN track t ON t.album_uri = rl.album_uri
    LEFT JOIN liked_track lt ON lt.track_uri = t.uri
    LEFT JOIN tmp_label_track_counts ltc ON ltc.standardized_label = rl.standardized_label
WHERE t.uri IN (SELECT track_uri FROM matching_track_uris)
GROUP BY rl.standardized_label, ltc.total_track_count, ltc.total_liked_track_count;