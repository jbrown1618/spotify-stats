SELECT
    pt.playlist_uri,
    p.name as playlist_name, 
    count(pt.track_uri) as playlist_track_count,
    count(lt.track_uri) as playlist_liked_track_count
FROM playlist_track pt
    INNER JOIN playlist p ON p.uri = pt.playlist_uri
    LEFT JOIN liked_track lt ON lt.track_uri = pt.track_uri
WHERE pt.track_uri in %(track_uris)s
GROUP BY pt.playlist_uri, p.name;