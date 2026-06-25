WITH track_stream_counts AS (
    SELECT
        'track' AS entity_type,
        t.uri AS entity_uri,
        COUNT(s.id)::INT AS stream_count
    FROM matching_track_uris m
        INNER JOIN track t ON t.uri = m.track_uri
        LEFT JOIN track_stream s
            ON s.track_uri = t.uri
            AND (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
            AND (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
    GROUP BY t.uri
),
album_stream_counts AS (
    SELECT
        'album' AS entity_type,
        al.uri AS entity_uri,
        COUNT(s.id)::INT AS stream_count
    FROM matching_track_uris m
        INNER JOIN track t ON t.uri = m.track_uri
        INNER JOIN album al ON al.uri = t.album_uri
        LEFT JOIN track_stream s
            ON s.track_uri = t.uri
            AND (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
            AND (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
    GROUP BY al.uri
),
artist_stream_counts AS (
    SELECT
        'artist' AS entity_type,
        a.uri AS entity_uri,
        COUNT(s.id)::INT AS stream_count
    FROM matching_track_uris m
        INNER JOIN track_artist ta ON ta.track_uri = m.track_uri
        INNER JOIN artist a ON a.uri = ta.artist_uri
        LEFT JOIN track_stream s
            ON s.track_uri = ta.track_uri
            AND (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
            AND (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
    GROUP BY a.uri
),
entity_stream_counts AS (
    SELECT * FROM track_stream_counts
    UNION ALL
    SELECT * FROM album_stream_counts
    UNION ALL
    SELECT * FROM artist_stream_counts
),
bucketed AS (
    SELECT
        entity_type,
        CASE
            WHEN stream_count = 0 THEN '0'
            WHEN stream_count = 1 THEN '1'
            WHEN stream_count = 2 THEN '2'
            WHEN stream_count BETWEEN 3 AND 5 THEN '3-5'
            WHEN stream_count BETWEEN 6 AND 10 THEN '6-10'
            WHEN stream_count BETWEEN 11 AND 20 THEN '11-20'
            WHEN stream_count BETWEEN 21 AND 50 THEN '21-50'
            WHEN stream_count BETWEEN 51 AND 100 THEN '51-100'
            ELSE '101+'
        END AS bucket,
        CASE
            WHEN stream_count = 0 THEN 0
            WHEN stream_count = 1 THEN 1
            WHEN stream_count = 2 THEN 2
            WHEN stream_count BETWEEN 3 AND 5 THEN 3
            WHEN stream_count BETWEEN 6 AND 10 THEN 6
            WHEN stream_count BETWEEN 11 AND 20 THEN 11
            WHEN stream_count BETWEEN 21 AND 50 THEN 21
            WHEN stream_count BETWEEN 51 AND 100 THEN 51
            ELSE 101
        END AS bucket_min,
        CASE
            WHEN stream_count = 0 THEN 0
            WHEN stream_count = 1 THEN 1
            WHEN stream_count = 2 THEN 2
            WHEN stream_count BETWEEN 3 AND 5 THEN 5
            WHEN stream_count BETWEEN 6 AND 10 THEN 10
            WHEN stream_count BETWEEN 11 AND 20 THEN 20
            WHEN stream_count BETWEEN 21 AND 50 THEN 50
            WHEN stream_count BETWEEN 51 AND 100 THEN 100
            ELSE NULL
        END AS bucket_max,
        CASE
            WHEN stream_count = 0 THEN 0
            WHEN stream_count = 1 THEN 1
            WHEN stream_count = 2 THEN 2
            WHEN stream_count BETWEEN 3 AND 5 THEN 3
            WHEN stream_count BETWEEN 6 AND 10 THEN 4
            WHEN stream_count BETWEEN 11 AND 20 THEN 5
            WHEN stream_count BETWEEN 21 AND 50 THEN 6
            WHEN stream_count BETWEEN 51 AND 100 THEN 7
            ELSE 8
        END AS bucket_sort
    FROM entity_stream_counts
)
SELECT
    entity_type,
    bucket,
    bucket_min,
    bucket_max,
    bucket_sort,
    COUNT(*)::INT AS item_count
FROM bucketed
GROUP BY entity_type, bucket, bucket_min, bucket_max, bucket_sort
ORDER BY entity_type, bucket_sort;
