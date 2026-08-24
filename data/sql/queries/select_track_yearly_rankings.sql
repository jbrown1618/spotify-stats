WITH yearly_counts AS (
    SELECT
        track_uri,
        EXTRACT(YEAR FROM played_at)::INTEGER AS year,
        COUNT(*) AS stream_count
    FROM track_stream
    GROUP BY track_uri, EXTRACT(YEAR FROM played_at)
),
ranked AS (
    SELECT
        track_uri,
        year,
        stream_count,
        ROW_NUMBER() OVER (
            PARTITION BY year
            ORDER BY stream_count DESC, track_uri
        ) AS yearly_rank
    FROM yearly_counts
)
SELECT year, yearly_rank, stream_count
FROM ranked
WHERE track_uri = :track_uri
    AND yearly_rank <= 10
ORDER BY year DESC;
