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
entity_maxes AS (
    SELECT
        entity_type,
        MAX(stream_count)::INT AS max_stream_count,
        LEAST(10, GREATEST(MAX(stream_count)::INT, 1)) AS bucket_count
    FROM entity_stream_counts
    GROUP BY entity_type
),
bucket_numbers AS (
    SELECT GENERATE_SERIES(1, 10)::INT AS bucket_number
),
positive_bucket_definitions AS (
    SELECT
        em.entity_type,
        bucket_number AS bucket_sort,
        (
            FLOOR(
                ((bucket_number - 1) * em.max_stream_count)::FLOAT
                / em.bucket_count
            )::INT
            + 1
        ) AS bucket_min,
        FLOOR(
            (bucket_number * em.max_stream_count)::FLOAT
            / em.bucket_count
        )::INT AS bucket_max
    FROM entity_maxes em
        CROSS JOIN bucket_numbers
    WHERE
        em.max_stream_count > 0
        AND bucket_number <= em.bucket_count
),
bucket_definitions AS (
    SELECT
        entity_type,
        0 AS bucket_sort,
        0 AS bucket_min,
        0 AS bucket_max
    FROM entity_maxes
    UNION ALL
    SELECT
        entity_type,
        bucket_sort,
        bucket_min,
        bucket_max
    FROM positive_bucket_definitions
),
bucketed_counts AS (
    SELECT
        esc.entity_type,
        CASE
            WHEN esc.stream_count = 0 THEN 0
            ELSE CEIL(
                (esc.stream_count * em.bucket_count::FLOAT)
                / em.max_stream_count
            )::INT
        END AS bucket_sort,
        COUNT(*)::INT AS item_count
    FROM entity_stream_counts esc
        INNER JOIN entity_maxes em ON em.entity_type = esc.entity_type
    GROUP BY esc.entity_type, bucket_sort
)
SELECT
    bd.entity_type,
    CASE
        WHEN bd.bucket_min = bd.bucket_max THEN bd.bucket_min::TEXT
        ELSE bd.bucket_min::TEXT || '-' || bd.bucket_max::TEXT
    END AS bucket,
    bd.bucket_min,
    bd.bucket_max,
    bd.bucket_sort,
    COALESCE(bc.item_count, 0)::INT AS item_count
FROM bucket_definitions bd
    LEFT JOIN bucketed_counts bc
        ON bc.entity_type = bd.entity_type
        AND bc.bucket_sort = bd.bucket_sort
ORDER BY bd.entity_type, bd.bucket_sort;
