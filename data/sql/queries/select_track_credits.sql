SELECT
    rc.credit_type,
    rc.credit_details,
    mb.artist_mbid,
    mb.artist_mb_name,
    mb.artist_sort_name,
    mb.artist_type,
    a.uri as artist_uri,
    a.name as artist_name,
    a.image_url as artist_image_url
FROM sp_track_mb_recording stmr
    INNER JOIN mb_recording_credit rc ON rc.recording_mbid = stmr.recording_mbid
    INNER JOIN mb_artist mb ON mb.artist_mbid = rc.artist_mbid
    LEFT JOIN sp_artist_mb_artist sama ON sama.artist_mbid = mb.artist_mbid
    LEFT JOIN artist a ON sama.spotify_artist_uri = a.uri
WHERE stmr.spotify_track_uri = :track_uri
ORDER BY 
    rc.credit_type,
    mb.artist_mb_name;
