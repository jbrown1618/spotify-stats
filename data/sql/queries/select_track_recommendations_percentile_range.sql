-- Find liked tracks matching the current filter whose total stream counts fall within
-- a given percentile range (e.g. low_percentile=0.5, high_percentile=0.7 for the
-- 50th-70th percentile), sorted with least-recently-streamed first.
-- Returns full track data (not just URIs). Pagination (limit/offset) is applied by the
-- caller in Python, matching the convention used by other paginated routes.
-- Parameters: low_percentile (0.0 to 1.0), high_percentile (0.0 to 1.0), filter_tracks (boolean)
WITH track_stats AS (
    SELECT
        s.track_uri,
        COUNT(*) AS total_streams,
        MAX(s.played_at) AS last_played
    FROM track_stream s
    WHERE (:filter_tracks = FALSE OR s.track_uri IN (SELECT track_uri FROM matching_track_uris))
      AND s.track_uri IN (SELECT track_uri FROM liked_track)
    GROUP BY s.track_uri
),
stream_percentiles AS (
    SELECT
        PERCENTILE_CONT(:low_percentile) WITHIN GROUP (ORDER BY total_streams) AS low_streams,
        PERCENTILE_CONT(:high_percentile) WITHIN GROUP (ORDER BY total_streams) AS high_streams
    FROM track_stats
),
matching_recs AS (
    SELECT ts.track_uri, ts.total_streams, ts.last_played
    FROM track_stats ts
    CROSS JOIN stream_percentiles sp
    WHERE ts.total_streams >= sp.low_streams
      AND ts.total_streams <= sp.high_streams
)
SELECT
    t.uri AS track_uri,
    t.name AS track_name,
    t.short_name AS track_short_name,
    t.popularity AS track_popularity,
    t.explicit AS track_explicit,
    t.duration_ms AS track_duration_ms,
    t.isrc AS track_isrc,
    t.uri IN (SELECT track_uri FROM liked_track) AS track_liked,
    mr.total_streams AS track_stream_count,
    mr.last_played AS track_last_played_at,

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

FROM matching_recs mr
    INNER JOIN track t ON t.uri = mr.track_uri
    INNER JOIN album al ON al.uri = t.album_uri
    INNER JOIN track_artist ta ON ta.track_uri = t.uri
    INNER JOIN artist a ON a.uri = ta.artist_uri

GROUP BY
    t.uri,
    t.name,
    t.short_name,
    t.popularity,
    t.explicit,
    t.duration_ms,
    t.isrc,
    mr.total_streams,
    mr.last_played,

    al.uri,
    al.name,
    al.short_name,
    al.album_type,
    al.label,
    al.popularity,
    al.release_date,
    al.image_url

ORDER BY mr.last_played ASC;
