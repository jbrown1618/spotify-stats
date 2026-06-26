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
stream_genres AS (
    SELECT DISTINCT
        ms.stream_id,
        ms.month_start,
        ag.genre
    FROM matching_streams ms
        INNER JOIN track_stream s ON s.id = ms.stream_id
        INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
        INNER JOIN artist_genre ag ON ag.artist_uri = ta.artist_uri
),
genre_totals AS (
    SELECT
        genre,
        COUNT(*) AS total_stream_count
    FROM stream_genres
    GROUP BY genre
),
top_genres AS (
    SELECT
        genre,
        ROW_NUMBER() OVER (ORDER BY total_stream_count DESC, genre) AS sort_order
    FROM genre_totals
    ORDER BY total_stream_count DESC, genre
    LIMIT :n
),
monthly_totals AS (
    SELECT
        month_start,
        COUNT(*)::FLOAT AS month_stream_count
    FROM matching_streams
    GROUP BY month_start
),
stream_top_genres AS (
    SELECT
        sg.stream_id,
        sg.month_start,
        tg.genre,
        tg.sort_order,
        COUNT(*) OVER (PARTITION BY sg.stream_id)::FLOAT AS top_genre_count
    FROM stream_genres sg
        INNER JOIN top_genres tg ON tg.genre = sg.genre
),
top_monthly AS (
    SELECT
        month_start,
        genre AS category_key,
        genre AS category_name,
        SUM(1.0 / top_genre_count)::FLOAT AS stream_count,
        sort_order
    FROM stream_top_genres
    GROUP BY month_start, genre, sort_order
),
top_stream_monthly AS (
    SELECT
        month_start,
        COUNT(DISTINCT stream_id)::FLOAT AS stream_count
    FROM stream_top_genres
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
