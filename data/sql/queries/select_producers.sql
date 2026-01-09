SELECT
    mb.artist_mb_name AS producer_name,
    mb.artist_mbid AS producer_mbid,
    a.uri as artist_uri,
    a.image_url as artist_image_url,
    ARRAY_AGG(DISTINCT rc.credit_type) as credit_types,
    COUNT(DISTINCT rc.recording_mbid) AS track_count,
    COUNT(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN rc.recording_mbid END) AS liked_track_count
FROM mb_recording_credit rc
    INNER JOIN mb_artist mb ON rc.artist_mbid = mb.artist_mbid
    INNER JOIN sp_track_mb_recording stmr ON rc.recording_mbid = stmr.recording_mbid
    LEFT JOIN liked_track lt ON stmr.spotify_track_uri = lt.track_uri
    LEFT JOIN sp_artist_mb_artist sama ON sama.artist_mbid = mb.artist_mbid
    LEFT JOIN artist a ON sama.spotify_artist_uri = a.uri
WHERE :filter_tracks = FALSE OR stmr.spotify_track_uri IN :track_uris
    AND rc.credit_type IN (
        'songwriter',
        'lyricist',
        'producer',
        'arranger',
        'sound',
        'mastering',
        'audio director',
        'video director',
        'publishing'
    ) 
GROUP BY
    mb.artist_mb_name,
    mb.artist_mbid,
    a.uri,
    a.image_url
ORDER BY track_count DESC, a.image_url NULLS LAST;