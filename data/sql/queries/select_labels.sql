SELECT DISTINCT rl.standardized_label
FROM record_label rl
WHERE :filter_albums = FALSE OR rl.album_uri IN :album_uris;