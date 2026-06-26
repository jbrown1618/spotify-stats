WITH artist_monthly AS (
    SELECT
        DATE_TRUNC('month', s.played_at) AS month_start,
        ta.artist_uri,
        a.name AS artist_name,
        COUNT(*)::INT AS stream_count
    FROM matching_track_uris m
        INNER JOIN track_stream s ON s.track_uri = m.track_uri
        INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
        INNER JOIN artist a ON a.uri = ta.artist_uri
    WHERE
        (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
        AND
        (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
    GROUP BY month_start, ta.artist_uri, a.name
),
artist_totals AS (
    SELECT
        artist_uri,
        artist_name,
        SUM(stream_count) AS total_stream_count
    FROM artist_monthly
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
        SUM(stream_count) AS month_stream_count
    FROM artist_monthly
    GROUP BY month_start
),
top_monthly AS (
    SELECT
        am.month_start,
        ta.artist_uri AS category_key,
        ta.artist_name AS category_name,
        am.stream_count,
        ta.sort_order
    FROM artist_monthly am
        INNER JOIN top_artists ta ON ta.artist_uri = am.artist_uri
),
other_monthly AS (
    SELECT
        mt.month_start,
        '__other__' AS category_key,
        'Other' AS category_name,
        (
            mt.month_stream_count
            - COALESCE(SUM(tm.stream_count), 0)
        )::INT AS stream_count,
        (:n + 1)::BIGINT AS sort_order
    FROM monthly_totals mt
        LEFT JOIN top_monthly tm ON tm.month_start = mt.month_start
    GROUP BY mt.month_start, mt.month_stream_count
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
