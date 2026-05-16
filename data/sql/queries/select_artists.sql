DROP TABLE IF EXISTS tmp_artist_stream_counts;

CREATE TEMPORARY TABLE tmp_artist_stream_counts AS
SELECT ta.artist_uri, COUNT(*) AS stream_count
FROM track_stream s
INNER JOIN track_artist ta
    ON ta.track_uri = s.track_uri
WHERE 
    (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
    AND 
    (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
GROUP BY ta.artist_uri;

DROP TABLE IF EXISTS tmp_artist_track_counts;

CREATE TEMPORARY TABLE tmp_artist_track_counts AS
SELECT
    ta.artist_uri,
    COUNT(DISTINCT ta.track_uri) AS total_track_count,
    COUNT(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN ta.track_uri END) AS total_liked_track_count,
    COUNT(DISTINCT CASE WHEN m.track_uri IS NOT NULL THEN ta.track_uri END) AS track_count,
    COUNT(DISTINCT CASE WHEN m.track_uri IS NOT NULL AND lt.track_uri IS NOT NULL THEN ta.track_uri END) AS liked_track_count
FROM track_artist ta
    INNER JOIN playlist_track pt ON pt.track_uri = ta.track_uri
    LEFT JOIN liked_track lt ON lt.track_uri = ta.track_uri
    LEFT JOIN matching_track_uris m ON m.track_uri = ta.track_uri
GROUP BY ta.artist_uri;

SELECT
    a.uri AS artist_uri,
    a.name AS artist_name,
    a.popularity AS artist_popularity,
    a.followers AS artist_followers,
    a.image_url AS artist_image_url,
    sc.stream_count AS artist_stream_count,
    COALESCE(tc.total_liked_track_count, 0) AS artist_total_liked_track_count,
    COALESCE(tc.liked_track_count, 0) AS artist_liked_track_count,
    COALESCE(tc.total_track_count, 0) AS artist_total_track_count,
    COALESCE(tc.track_count, 0) AS artist_track_count

FROM artist a
    INNER JOIN track_artist ta ON ta.artist_uri = a.uri
    INNER JOIN playlist_track pt ON ta.track_uri = pt.track_uri
    LEFT JOIN sp_artist_mb_artist sp_mb_a ON sp_mb_a.spotify_artist_uri = a.uri
    LEFT JOIN mb_artist mba ON mba.artist_mbid = sp_mb_a.artist_mbid
    LEFT JOIN tmp_artist_stream_counts sc ON sc.artist_uri = a.uri
    LEFT JOIN tmp_artist_track_counts tc ON tc.artist_uri = a.uri
WHERE
    (:filter_artists = FALSE OR a.uri IN :artist_uris)
    AND
    ta.track_uri IN (SELECT track_uri FROM matching_track_uris)
    AND
    (:filter_mbids = FALSE OR mba.artist_mbid IN :mbids)
    AND
    ((:wrapped_start_date IS NULL AND :wrapped_end_date IS NULL) OR sc.stream_count IS NOT NULL)
GROUP BY
    a.uri,
    a.name,
    a.popularity,
    a.followers,
    a.image_url,
    sc.stream_count,
    tc.total_liked_track_count,
    tc.liked_track_count,
    tc.total_track_count,
    tc.track_count

ORDER BY sc.stream_count DESC NULLS LAST;