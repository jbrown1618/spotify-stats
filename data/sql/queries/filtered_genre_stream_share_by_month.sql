WITH stream_genres AS (
    SELECT DISTINCT
        s.id AS stream_id,
        DATE_TRUNC('month', s.played_at) AS month_start,
        ag.genre
    FROM matching_track_uris m
        INNER JOIN track_stream s ON s.track_uri = m.track_uri
        INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
        INNER JOIN artist_genre ag ON ag.artist_uri = ta.artist_uri
    WHERE
        (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
        AND
        (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
),
genre_monthly AS (
    SELECT
        month_start,
        genre,
        COUNT(*)::INT AS stream_count
    FROM stream_genres
    GROUP BY month_start, genre
),
genre_totals AS (
    SELECT
        genre,
        SUM(stream_count) AS total_stream_count
    FROM genre_monthly
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
        SUM(stream_count) AS month_stream_count
    FROM genre_monthly
    GROUP BY month_start
),
top_monthly AS (
    SELECT
        gm.month_start,
        tg.genre AS category_key,
        tg.genre AS category_name,
        gm.stream_count,
        tg.sort_order
    FROM genre_monthly gm
        INNER JOIN top_genres tg ON tg.genre = gm.genre
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
