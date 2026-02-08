-- Update streams from orphan track to replacement track in track_stream table,
-- but only where the replacement doesn't already have a stream at that played_at time
UPDATE track_stream ts1
SET track_uri = %(replacement_uri)s
WHERE track_uri = %(orphan_uri)s
AND NOT EXISTS (
    SELECT 1 FROM track_stream
    WHERE track_uri = %(replacement_uri)s
    AND played_at = ts1.played_at
);

-- Delete any orphan streams that would cause duplicates (replacement already has a stream at that time)
DELETE FROM track_stream ts1
WHERE track_uri = %(orphan_uri)s
AND EXISTS (
    SELECT 1 FROM track_stream ts2
    WHERE ts2.track_uri = %(replacement_uri)s
    AND ts2.played_at = ts1.played_at
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