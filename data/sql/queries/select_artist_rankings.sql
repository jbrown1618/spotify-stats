WITH yearly_counts AS (
    SELECT
        EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
        ta.artist_uri,
        COUNT(*) AS stream_count
    FROM track_stream s
    INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
    GROUP BY year, ta.artist_uri
),
period_counts AS (
    SELECT year, artist_uri, stream_count
    FROM yearly_counts
    UNION ALL
    SELECT
        NULL AS year,
        artist_uri,
        SUM(stream_count) AS stream_count
    FROM yearly_counts
    GROUP BY artist_uri
),
ranked AS (
    SELECT
        year,
        artist_uri,
        stream_count,
        RANK() OVER (
            PARTITION BY year
            ORDER BY stream_count DESC
        )::INTEGER AS rank
    FROM period_counts
)
SELECT year, rank, stream_count
FROM ranked
WHERE artist_uri = :entity_uri
    AND rank <= 100
ORDER BY year DESC NULLS FIRST;
