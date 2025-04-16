SELECT
    mb.artist_mb_name AS producer_name,
    mb.artist_mbid AS producer_uri,
    COUNT(DISTINCT rc.recording_mbid) AS track_count,
    COUNT(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN rc.recording_mbid END) AS liked_track_count
FROM mb_recording_credit rc
    INNER JOIN mb_artist mb ON rc.artist_mbid = mb.artist_mbid
    LEFT JOIN sp_track_mb_recording stmr ON rc.recording_mbid = stmr.recording_mbid
    LEFT JOIN liked_track lt ON stmr.spotify_track_uri = lt.track_uri
WHERE rc.credit_type = 'producer'
GROUP BY mb.artist_mb_name, mb.artist_mbid
ORDER BY track_count DESC;