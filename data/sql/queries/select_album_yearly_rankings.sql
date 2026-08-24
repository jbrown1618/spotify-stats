WITH yearly_counts AS (
    SELECT
        t.album_uri,
        EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
        COUNT(*) AS stream_count
    FROM track_stream s
    INNER JOIN track t ON t.uri = s.track_uri
    GROUP BY t.album_uri, EXTRACT(YEAR FROM s.played_at)
),
ranked AS (
    SELECT
        album_uri,
        year,
        stream_count,
        ROW_NUMBER() OVER (
            PARTITION BY year
            ORDER BY stream_count DESC, album_uri
        ) AS yearly_rank
    FROM yearly_counts
)
SELECT year, yearly_rank, stream_count
FROM ranked
WHERE album_uri = :album_uri
    AND yearly_rank <= 10
ORDER BY year DESC;
