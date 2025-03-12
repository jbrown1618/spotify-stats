SELECT album_uri, array_agg(artist_uri)
FROM album_artist
WHERE album_uri in %(album_uris)s
GROUP BY album_uri