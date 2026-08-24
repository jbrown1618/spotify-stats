WITH yearly_counts AS (
    SELECT
        ta.artist_uri,
        EXTRACT(YEAR FROM s.played_at)::INTEGER AS year,
        COUNT(*) AS stream_count
    FROM track_stream s
    INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
    GROUP BY ta.artist_uri, EXTRACT(YEAR FROM s.played_at)
),
ranked AS (
    SELECT
        artist_uri,
        year,
        stream_count,
        ROW_NUMBER() OVER (
            PARTITION BY year
            ORDER BY stream_count DESC, artist_uri
        ) AS yearly_rank
    FROM yearly_counts
)
SELECT year, yearly_rank, stream_count
FROM ranked
WHERE artist_uri = :artist_uri
    AND yearly_rank <= 10
ORDER BY year DESC;
