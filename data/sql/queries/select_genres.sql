SELECT DISTINCT ag.genre
FROM artist_genre ag
WHERE :filter_artists = FALSE OR ag.artist_uri IN :artist_uris;