SELECT track_uri, array_agg(artist_uri)
FROM track_artist
WHERE track_uri in :track_uris
GROUP BY track_uri;