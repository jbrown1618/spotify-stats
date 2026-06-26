WITH matching_streams AS (
    SELECT
        s.id AS stream_id,
        DATE_TRUNC('month', s.played_at) AS month_start
    FROM matching_track_uris m
        INNER JOIN track_stream s ON s.track_uri = m.track_uri
    WHERE
        (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
        AND
        (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
),
stream_artists AS (
    SELECT DISTINCT
        ms.stream_id,
        ms.month_start,
        ta.artist_uri,
        a.name AS artist_name
    FROM matching_streams ms
        INNER JOIN track_stream s ON s.id = ms.stream_id
        INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
        INNER JOIN artist a ON a.uri = ta.artist_uri
),
artist_totals AS (
    SELECT
        artist_uri,
        artist_name,
        COUNT(*) AS total_stream_count
    FROM stream_artists
    GROUP BY artist_uri, artist_name
),
top_artists AS (
    SELECT
        artist_uri,
        artist_name,
        ROW_NUMBER() OVER (ORDER BY total_stream_count DESC, artist_name) AS sort_order
    FROM artist_totals
    ORDER BY total_stream_count DESC, artist_name
    LIMIT :n
),
monthly_totals AS (
    SELECT
        month_start,
        COUNT(*)::FLOAT AS month_stream_count
    FROM matching_streams
    GROUP BY month_start
),
stream_top_artists AS (
    SELECT
        sa.stream_id,
        sa.month_start,
        ta.artist_uri,
        ta.artist_name,
        ta.sort_order,
        COUNT(*) OVER (PARTITION BY sa.stream_id)::FLOAT AS top_artist_count
    FROM stream_artists sa
        INNER JOIN top_artists ta ON ta.artist_uri = sa.artist_uri
),
top_monthly AS (
    SELECT
        month_start,
        artist_uri AS category_key,
        artist_name AS category_name,
        SUM(1.0 / top_artist_count)::FLOAT AS stream_count,
        sort_order
    FROM stream_top_artists
    GROUP BY month_start, artist_uri, artist_name, sort_order
),
top_stream_monthly AS (
    SELECT
        month_start,
        COUNT(DISTINCT stream_id)::FLOAT AS stream_count
    FROM stream_top_artists
    GROUP BY month_start
),
other_monthly AS (
    SELECT
        mt.month_start,
        '__other__' AS category_key,
        'Other' AS category_name,
        (
            mt.month_stream_count
            - COALESCE(tsm.stream_count, 0)
        )::FLOAT AS stream_count,
        (:n + 1)::BIGINT AS sort_order
    FROM monthly_totals mt
        LEFT JOIN top_stream_monthly tsm ON tsm.month_start = mt.month_start
),
share_rows AS (
    SELECT * FROM top_monthly
    UNION ALL
    SELECT * FROM other_monthly WHERE stream_count > 0
)
SELECT
    TO_CHAR(sr.month_start, 'YYYY-MM') AS month,
    sr.category_key,
    sr.category_name,
    sr.stream_count,
    (sr.stream_count::FLOAT / mt.month_stream_count)::FLOAT AS stream_share,
    sr.sort_order::INT
FROM share_rows sr
    INNER JOIN monthly_totals mt ON mt.month_start = sr.month_start
ORDER BY sr.month_start, sr.sort_order;
