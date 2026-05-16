DROP TABLE IF EXISTS tmp_stream_counts;

CREATE TEMPORARY TABLE tmp_stream_counts AS
SELECT s.track_uri, COUNT(*) AS stream_count, MAX(s.played_at) AS last_played_at
FROM track_stream s
WHERE 
    (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
    AND 
    (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
GROUP BY s.track_uri;

SELECT
    t.uri AS track_uri,
    t.name AS track_name,
    t.short_name AS track_short_name,
    t.popularity AS track_popularity,
    t.explicit AS track_explicit,
    t.duration_ms AS track_duration_ms,
    t.isrc AS track_isrc,
    t.uri IN (SELECT track_uri FROM liked_track) AS track_liked,
    sc.stream_count AS track_stream_count,
    sc.last_played_at AS track_last_played_at,

    ARRAY_AGG(DISTINCT a.name) AS artist_names,
    ARRAY_AGG(DISTINCT a.uri) AS artist_uris,

    al.uri AS album_uri,
    al.name AS album_name,
    al.short_name AS album_short_name,
    al.album_type,
    al.label AS album_label,
    al.popularity AS album_popularity,
    al.release_date AS album_release_date,
    al.image_url AS album_image_url,
    (
        CASE
        WHEN LENGTH(al.release_date) = 10
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM-DD'))
        WHEN LENGTH(al.release_date) = 7
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM'))
        WHEN LENGTH(al.release_date) = 4
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY'))
        ELSE 0
        END
    ) AS album_release_year

FROM track t
    INNER JOIN album al ON al.uri = t.album_uri
    INNER JOIN track_artist ta ON ta.track_uri = t.uri
    INNER JOIN artist a ON a.uri = ta.artist_uri
    LEFT JOIN tmp_stream_counts sc ON sc.track_uri = t.uri

WHERE
    t.uri IN (SELECT track_uri FROM matching_track_uris)
    AND
    ((:wrapped_start_date IS NULL AND :wrapped_end_date IS NULL) OR sc.stream_count IS NOT NULL)

GROUP BY
    t.uri,
    t.name,
    t.short_name,
    t.popularity,
    t.explicit,
    t.duration_ms,
    t.isrc,
    sc.stream_count,
    sc.last_played_at,

    al.uri,
    al.name,
    al.short_name,
    al.album_type,
    al.label,
    al.popularity,
    al.release_date,
    al.image_url

ORDER BY track_stream_count DESC NULLS LAST;
