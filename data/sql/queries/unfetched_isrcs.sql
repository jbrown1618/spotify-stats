SELECT t.uri, t.isrc
FROM track t
    INNER JOIN liked_track lt
        ON lt.track_uri = t.uri 
    LEFT JOIN sp_track_mb_recording stmr
        ON stmr.spotify_track_uri = t.uri
    LEFT JOIN mb_unfetchable_isrc mbui
        ON t.isrc = mbui.isrc
WHERE mbui.isrc IS NOT NULL
    AND stmr.spotify_track_uri IS NULL;