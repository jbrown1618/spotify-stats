SELECT
    t.uri,
    t.name
FROM track t
INNER JOIN track_artist ta
    ON ta.track_uri = t.uri
    AND ta.artist_index = 0
INNER JOIN artist a ON a.uri = ta.artist_uri
INNER JOIN playlist_track pt ON pt.track_uri = t.uri
WHERE t.name = %(track_name)s
    AND a.name = %(artist_name)s
LIMIT 1;
