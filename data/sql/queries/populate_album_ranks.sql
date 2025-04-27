DROP TABLE IF EXISTS total_album_streams_for_date;

CREATE TEMPORARY TABLE total_album_streams_for_date AS
SELECT t.album_uri,
       SUM(stream_count) AS stream_count
FROM listening_history h
INNER JOIN listening_period p ON p.id = h.listening_period_id
INNER JOIN track t ON t.uri = h.track_uri
WHERE p.from_time <= %(as_of_date)s
GROUP BY t.album_uri;

INSERT INTO album_rank (album_uri, stream_count, rank, as_of_date)
SELECT album_uri,
       stream_count,
       ROW_NUMBER() OVER(ORDER BY stream_count DESC, album_uri ASC) AS rank,
       %(as_of_date)s AS as_of_date
FROM total_album_streams_for_date
ON CONFLICT DO NOTHING;