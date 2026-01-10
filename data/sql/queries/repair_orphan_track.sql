-- Update all streams from orphan track to replacement track in track_stream table
UPDATE track_stream
SET track_uri = %(replacement_uri)s
WHERE track_uri = %(orphan_uri)s;

-- Also update the legacy listening_history table (dual-write during migration)
UPDATE listening_history h
SET track_uri = %(replacement_uri)s
WHERE h.track_uri = %(orphan_uri)s
AND NOT EXISTS (
    SELECT track_uri
    FROM listening_history
    WHERE track_uri = %(replacement_uri)s
    AND listening_period_id = h.listening_period_id
);

-- If the listening period has both the orphan and replacement
-- version of the track, add the orphan totals to the
-- replacement version.      
UPDATE listening_history h
SET stream_count = h.stream_count + (
    SELECT stream_count
    FROM listening_history
    WHERE track_uri = %(orphan_uri)s
    AND listening_period_id = h.listening_period_id
)
WHERE h.track_uri = %(replacement_uri)s
AND EXISTS (
    SELECT track_uri
    FROM listening_history
    WHERE track_uri = %(orphan_uri)s
    AND listening_period_id = h.listening_period_id
);

-- If the listening period has both the orphan and replacement
-- version of the track, we have merged them above so we can
-- now delete the orphan version.
DELETE FROM listening_history h
WHERE track_uri = %(orphan_uri)s
AND EXISTS (
    SELECT track_uri
    FROM listening_history
    WHERE track_uri = %(replacement_uri)s
    AND listening_period_id = h.listening_period_id   
);

UPDATE sp_track_mb_recording r
SET spotify_track_uri = %(replacement_uri)s
WHERE r.spotify_track_uri = %(orphan_uri)s
AND NOT EXISTS (
    SELECT spotify_track_uri
    FROM sp_track_mb_recording
    WHERE spotify_track_uri = r.spotify_track_uri
    AND recording_mbid = r.recording_mbid
);

DELETE FROM track
WHERE uri = %(orphan_uri)s;

DELETE FROM track_artist
WHERE track_uri = %(orphan_uri)s;