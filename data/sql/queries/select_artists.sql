DROP TABLE IF EXISTS tmp_artist_stream_counts;

CREATE TEMPORARY TABLE tmp_artist_stream_counts AS
SELECT ta.artist_uri, SUM(h.stream_count) AS stream_count
FROM listening_history h
INNER JOIN listening_period p
    ON h.listening_period_id = p.id
INNER JOIN track_artist ta
    ON ta.track_uri = h.track_uri
WHERE 
    (:wrapped_start_date IS NULL OR :wrapped_start_date <= p.to_time)
    AND 
    (:wrapped_end_date IS NULL OR :wrapped_end_date >= p.from_time)
GROUP BY ta.artist_uri;

SELECT
    a.uri AS artist_uri,
    a.name AS artist_name,
    a.popularity AS artist_popularity,
    a.followers AS artist_followers,
    a.image_url AS artist_image_url,
    sc.stream_count AS artist_stream_count,
    (
        SELECT COUNT(track_uri) 
        FROM (
            SELECT DISTINCT ita.track_uri
            FROM track_artist ita 
            INNER JOIN liked_track ilt ON ilt.track_uri = ita.track_uri
            WHERE ita.artist_uri = a.uri
            AND ita.track_uri IN (
                SELECT track_uri FROM playlist_track
            )
        )
    ) AS artist_total_liked_track_count,
    (
        SELECT COUNT(track_uri) 
        FROM (
            SELECT DISTINCT ita.track_uri
            FROM track_artist ita 
            INNER JOIN liked_track ilt ON ilt.track_uri = ita.track_uri
            WHERE ita.artist_uri = a.uri
            AND (:filter_tracks = FALSE OR ita.track_uri IN :track_uris)
        )
    ) AS artist_liked_track_count,
    (
        SELECT COUNT(track_uri) 
        FROM (
            SELECT DISTINCT ita.track_uri
            FROM track_artist ita 
            WHERE ita.artist_uri = a.uri
            AND ita.track_uri IN (
                SELECT track_uri FROM playlist_track
            )
        )
    ) AS artist_total_track_count,
    (
        SELECT COUNT(track_uri) 
        FROM (
            SELECT DISTINCT ita.track_uri
            FROM track_artist ita 
            WHERE ita.artist_uri = a.uri
            AND (:filter_tracks = FALSE OR ita.track_uri IN :track_uris)
        )
    ) AS artist_track_count

FROM artist a
    INNER JOIN track_artist ta ON ta.artist_uri = a.uri
    INNER JOIN playlist_track pt ON ta.track_uri = pt.track_uri
    LEFT JOIN sp_artist_mb_artist sp_mb_a ON sp_mb_a.spotify_artist_uri = a.uri
    LEFT JOIN mb_artist mba ON mba.artist_mbid = sp_mb_a.artist_mbid
    LEFT JOIN tmp_artist_stream_counts sc ON sc.artist_uri = a.uri
WHERE
    (:filter_artists = FALSE OR a.uri IN :artist_uris)
    AND
    (:filter_tracks = FALSE OR ta.track_uri IN :track_uris)
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
    sc.stream_count

ORDER BY sc.stream_count DESC NULLS LAST;