SELECT
    rl.standardized_label as label, 
    count(t.uri) as label_track_count,
    (
        SELECT COUNT(it.uri)
        FROM track it
            INNER JOIN record_label irl ON irl.album_uri = it.album_uri
        WHERE irl.standardized_label = rl.standardized_label
    ) as label_total_track_count,
    count(lt.track_uri) as label_liked_track_count,
    (
        SELECT COUNT(it.uri)
        FROM track it
            INNER JOIN liked_track ilt ON ilt.track_uri = it.uri
            INNER JOIN record_label irl ON irl.album_uri = it.album_uri
        WHERE irl.standardized_label = rl.standardized_label
    ) as label_total_liked_track_count
FROM record_label rl
    INNER JOIN track t ON t.album_uri = rl.album_uri
    LEFT JOIN liked_track lt ON lt.track_uri = t.uri
WHERE t.uri IN %(track_uris)s
GROUP BY rl.standardized_label;