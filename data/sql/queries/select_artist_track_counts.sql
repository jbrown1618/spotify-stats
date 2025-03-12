SELECT
    ta.artist_uri,
    a.name as artist_name, 
    count(ta.track_uri) as artist_track_count,
    count(lt.track_uri) as artist_liked_track_count
FROM track_artist ta
    INNER JOIN artist a ON a.uri = ta.artist_uri
    LEFT JOIN liked_track lt ON lt.track_uri = ta.track_uri
WHERE ta.track_uri in %(track_uris)s
GROUP BY ta.artist_uri, a.name;