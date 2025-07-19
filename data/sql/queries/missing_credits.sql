SELECT t.uri, t.isrc
FROM track t
INNER JOIN sp_track_mb_recording stmr
    ON stmr.spotify_track_uri = t.uri
INNER JOIN mb_recording r
    ON r.recording_mbid = stmr.recording_mbid
WHERE NOT EXISTS(
    SELECT *
    FROM mb_recording_credit rc
    WHERE rc.recording_mbid = r.recording_mbid
)