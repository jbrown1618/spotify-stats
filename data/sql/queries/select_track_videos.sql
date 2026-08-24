SELECT DISTINCT ON (dv.uri)
    dv.uri,
    dv.title,
    dv.description,
    dv.duration_seconds,
    dv.embed,
    dv.discogs_master_id
FROM sp_track_discogs_track mapping
INNER JOIN discogs_video dv
    ON dv.discogs_master_id = mapping.discogs_master_id
    AND dv.track_position = mapping.discogs_track_position
WHERE mapping.spotify_track_uri = :track_uri
    AND (
        LOWER(dv.uri) LIKE '%youtube.com%'
        OR LOWER(dv.uri) LIKE '%youtu.be%'
    )
ORDER BY dv.uri, dv.title;
