DROP TABLE IF EXISTS total_track_streams_for_date;

CREATE TEMPORARY TABLE total_track_streams_for_date AS
SELECT s.track_uri,
       COUNT(*) AS stream_count
FROM track_stream s
WHERE s.played_at <= %(as_of_date)s
GROUP BY s.track_uri;

INSERT INTO track_rank (track_uri, stream_count, rank, as_of_date)
SELECT track_uri,
       stream_count,
       ROW_NUMBER() OVER(ORDER BY stream_count DESC, track_uri ASC) AS rank,
       %(as_of_date)s AS as_of_date
FROM total_track_streams_for_date
ON CONFLICT DO NOTHING;