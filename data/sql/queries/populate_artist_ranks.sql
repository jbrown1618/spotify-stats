DROP TABLE IF EXISTS total_artist_streams_for_date;

CREATE TEMPORARY TABLE total_artist_streams_for_date AS
SELECT ta.artist_uri,
       SUM(stream_count) AS stream_count
FROM listening_history h
INNER JOIN listening_period p ON p.id = h.listening_period_id
INNER JOIN track_artist ta ON ta.track_uri = h.track_uri
WHERE p.from_time <= %(as_of_date)s
GROUP BY ta.artist_uri;

INSERT INTO artist_rank (artist_uri, stream_count, rank, as_of_date)
SELECT artist_uri,
       stream_count,
       ROW_NUMBER() OVER(ORDER BY stream_count DESC, artist_uri ASC) AS rank,
       %(as_of_date)s AS as_of_date
FROM total_artist_streams_for_date
ON CONFLICT DO NOTHING;