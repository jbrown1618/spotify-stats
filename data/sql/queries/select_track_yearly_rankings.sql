WITH yearly_counts AS (
    SELECT
        EXTRACT(YEAR FROM played_at)::INTEGER AS year,
        track_uri,
        COUNT(*) AS stream_count
    FROM track_stream
    GROUP BY year, track_uri
),
ranked AS (
    SELECT
        year,
        track_uri,
        stream_count,
        RANK() OVER (
            PARTITION BY year
            ORDER BY stream_count DESC
        )::INTEGER AS rank
    FROM yearly_counts
)
SELECT year, rank, stream_count
FROM ranked
WHERE track_uri = :entity_uri
    AND rank <= 100
ORDER BY year DESC;
