SELECT ta.artist_uri, array_agg(t.album_uri)
FROM track_artist ta
    INNER JOIN track t ON t.uri = ta.track_uri
WHERE ta.artist_uri in %(artist_uris)s
GROUP BY ta.artist_uri;