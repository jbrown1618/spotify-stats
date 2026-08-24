WITH yearly_counts AS (
    SELECT
        EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
        t.album_uri,
        COUNT(*) AS stream_count
    FROM track_stream s
    INNER JOIN track t ON t.uri = s.track_uri
    GROUP BY year, t.album_uri
),
period_counts AS (
    SELECT year, album_uri, stream_count
    FROM yearly_counts
    UNION ALL
    SELECT
        NULL AS year,
        album_uri,
        SUM(stream_count) AS stream_count
    FROM yearly_counts
    GROUP BY album_uri
),
ranked AS (
    SELECT
        year,
        album_uri,
        stream_count,
        RANK() OVER (
            PARTITION BY year
            ORDER BY stream_count DESC
        )::INTEGER AS rank
    FROM period_counts
)
SELECT year, rank, stream_count
FROM ranked
WHERE album_uri = :entity_uri
    AND rank <= 100
ORDER BY year DESC NULLS FIRST;
