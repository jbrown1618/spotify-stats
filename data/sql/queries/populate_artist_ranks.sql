DROP TABLE IF EXISTS total_artist_streams_for_date;

CREATE TEMPORARY TABLE total_artist_streams_for_date AS
SELECT ta.artist_uri,
       COUNT(*) AS stream_count
FROM track_stream s
INNER JOIN track_artist ta ON ta.track_uri = s.track_uri
WHERE s.played_at <= %(as_of_date)s
GROUP BY ta.artist_uri;

INSERT INTO artist_rank (artist_uri, stream_count, rank, as_of_date)
SELECT artist_uri,
       stream_count,
       ROW_NUMBER() OVER(ORDER BY stream_count DESC, artist_uri ASC) AS rank,
       %(as_of_date)s AS as_of_date
FROM total_artist_streams_for_date
ON CONFLICT DO NOTHING;