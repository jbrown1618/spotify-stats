SELECT
    t.uri AS track_uri,
    t.name AS track_name,
    'musicbrainz' AS source,
    mr.recording_mbid AS source_id,
    mr.recording_title AS source_title,
    mr.recording_language AS language,
    NULL::TEXT AS position
FROM track t
INNER JOIN sp_track_mb_recording mapping
    ON mapping.spotify_track_uri = t.uri
INNER JOIN mb_recording mr
    ON mr.recording_mbid = mapping.recording_mbid
WHERE t.album_uri = :album_uri

UNION ALL

SELECT
    t.uri AS track_uri,
    t.name AS track_name,
    'discogs' AS source,
    mapping.discogs_master_id::TEXT AS source_id,
    mapping.discogs_track_title AS source_title,
    NULL::TEXT AS language,
    mapping.discogs_track_position AS position
FROM track t
INNER JOIN sp_track_discogs_track mapping
    ON mapping.spotify_track_uri = t.uri
WHERE t.album_uri = :album_uri

ORDER BY track_name, source, position;
