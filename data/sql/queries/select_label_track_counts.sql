SELECT
    rl.standardized_label as label, 
    count(t.uri) as label_track_count,
    count(lt.track_uri) as label_liked_track_count
FROM record_label rl
    INNER JOIN track t ON t.album_uri = rl.album_uri
    LEFT JOIN liked_track lt ON lt.track_uri = t.uri
WHERE t.uri in %(track_uris)s
GROUP BY rl.standardized_label;