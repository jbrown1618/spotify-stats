SELECT
    rc.recording_mbid,
    rc.credit_type,
    rc.credit_details,
    mr.recording_title,
    stmr.spotify_track_uri,
    t.name as track_name,
    t.uri as track_uri
FROM mb_recording_credit rc
    INNER JOIN mb_recording mr ON rc.recording_mbid = mr.recording_mbid
    INNER JOIN sp_track_mb_recording stmr ON rc.recording_mbid = stmr.recording_mbid
    LEFT JOIN track t ON stmr.spotify_track_uri = t.uri
WHERE rc.artist_mbid IN (
    SELECT artist_mbid 
    FROM sp_artist_mb_artist 
    WHERE spotify_artist_uri = :artist_uri
)
ORDER BY rc.credit_type, mr.recording_title;
