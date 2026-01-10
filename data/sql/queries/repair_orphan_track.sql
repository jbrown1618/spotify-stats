-- Update all streams from orphan track to replacement track
UPDATE track_stream
SET track_uri = %(replacement_uri)s
WHERE track_uri = %(orphan_uri)s;

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