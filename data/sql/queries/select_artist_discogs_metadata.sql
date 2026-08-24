SELECT
    da.discogs_artist_id,
    da.name,
    da.realname,
    da.profile,
    da.primary_image_url,
    COALESCE(da.namevariations, '[]'::JSONB) AS namevariations
FROM sp_artist_discogs_artist mapping
INNER JOIN discogs_artist da
    ON da.discogs_artist_id = mapping.discogs_artist_id
WHERE mapping.spotify_artist_uri = :artist_uri
ORDER BY da.name;
