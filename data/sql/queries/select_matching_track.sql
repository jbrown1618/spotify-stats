SELECT t.uri, t.name
FROM track t
INNER JOIN track_artist ta ON ta.track_uri = t.uri AND ta.artist_index = 0
INNER JOIN track orphan ON orphan.uri = %(orphan_uri)s
INNER JOIN track_artist orphanta ON orphanta.track_uri = orphan.uri AND orphanta.artist_index = 0
WHERE
    (
        t.name = orphan.name
        OR t.short_name = orphan.short_name
        OR (t.isrc IS NOT NULL AND t.isrc = orphan.isrc)
    )
    AND ta.artist_uri = orphanta.artist_uri
    AND t.uri IN (
    SELECT pt.track_uri FROM playlist_track pt
);