DROP TABLE IF EXISTS total_album_streams_for_date;

CREATE TEMPORARY TABLE total_album_streams_for_date AS
SELECT t.album_uri,
       COUNT(*) AS stream_count
FROM track_stream s
INNER JOIN track t ON t.uri = s.track_uri
WHERE s.played_at <= %(as_of_date)s
GROUP BY t.album_uri;

INSERT INTO album_rank (album_uri, stream_count, rank, as_of_date)
SELECT album_uri,
       stream_count,
       ROW_NUMBER() OVER(ORDER BY stream_count DESC, album_uri ASC) AS rank,
       %(as_of_date)s AS as_of_date
FROM total_album_streams_for_date
ON CONFLICT DO NOTHING;