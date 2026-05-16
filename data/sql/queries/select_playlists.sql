DROP TABLE IF EXISTS tmp_playlist_track_counts;

CREATE TEMPORARY TABLE tmp_playlist_track_counts AS
SELECT
    pt.playlist_uri,
    COUNT(pt.track_uri) AS total_track_count,
    COUNT(lt.track_uri) AS total_liked_track_count,
    COUNT(CASE WHEN m.track_uri IS NOT NULL THEN pt.track_uri END) AS track_count,
    COUNT(CASE WHEN m.track_uri IS NOT NULL AND lt.track_uri IS NOT NULL THEN pt.track_uri END) AS liked_track_count
FROM playlist_track pt
    LEFT JOIN liked_track lt ON lt.track_uri = pt.track_uri
    LEFT JOIN matching_track_uris m ON m.track_uri = pt.track_uri
GROUP BY pt.playlist_uri;

SELECT
    p.uri AS playlist_uri,
    p.name AS playlist_name,
    p.collaborative AS playlist_collaborative,
    p.public AS playlist_public,
    p.image_url AS playlist_image_url,
    p.owner AS playlist_owner,
    COALESCE(tc.track_count, 0) AS playlist_track_count,
    COALESCE(tc.total_track_count, 0) AS playlist_total_track_count,
    COALESCE(tc.liked_track_count, 0) AS playlist_liked_track_count,
    COALESCE(tc.total_liked_track_count, 0) AS playlist_total_liked_track_count
FROM playlist p
    INNER JOIN tmp_playlist_track_counts tc ON tc.playlist_uri = p.uri
WHERE tc.track_count > 0;