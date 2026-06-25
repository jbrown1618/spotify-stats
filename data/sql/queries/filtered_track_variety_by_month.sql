WITH monthly_track_counts AS (
    SELECT
        DATE_TRUNC('month', s.played_at) AS month_start,
        s.track_uri,
        COUNT(*)::FLOAT AS stream_count
    FROM matching_track_uris m
        INNER JOIN track_stream s ON s.track_uri = m.track_uri
    WHERE
        (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
        AND
        (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
    GROUP BY month_start, s.track_uri
),
ranked_track_counts AS (
    SELECT
        month_start,
        track_uri,
        stream_count,
        ROW_NUMBER() OVER (
            PARTITION BY month_start
            ORDER BY stream_count DESC, track_uri
        ) AS stream_rank
    FROM monthly_track_counts
),
monthly_totals AS (
    SELECT
        month_start,
        SUM(stream_count) AS total_stream_count,
        COUNT(*)::INT AS unique_track_count
    FROM monthly_track_counts
    GROUP BY month_start
)
SELECT
    TO_CHAR(rtc.month_start, 'YYYY-MM') AS month,
    mt.total_stream_count::INT AS total_stream_count,
    mt.unique_track_count,
    EXP(
        -SUM(
            (rtc.stream_count / mt.total_stream_count)
            * LN(rtc.stream_count / mt.total_stream_count)
        )
    )::FLOAT AS effective_track_count,
    (
        SUM(CASE WHEN rtc.stream_rank <= 10 THEN rtc.stream_count ELSE 0 END)
        / mt.total_stream_count
    )::FLOAT AS top_10_stream_share
FROM ranked_track_counts rtc
    INNER JOIN monthly_totals mt ON mt.month_start = rtc.month_start
GROUP BY rtc.month_start, mt.total_stream_count, mt.unique_track_count
ORDER BY rtc.month_start;
