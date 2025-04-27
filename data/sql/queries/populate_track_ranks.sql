DROP TABLE IF EXISTS total_track_streams_for_date;

CREATE TEMPORARY TABLE total_track_streams_for_date AS
SELECT h.track_uri,
       SUM(stream_count) AS stream_count
FROM listening_history h
INNER JOIN listening_period p ON p.id = h.listening_period_id
WHERE p.from_time <= %(as_of_date)s
GROUP BY h.track_uri;

INSERT INTO track_rank (track_uri, stream_count, rank, as_of_date)
SELECT track_uri,
       stream_count,
       ROW_NUMBER() OVER(ORDER BY stream_count DESC, track_uri ASC) AS rank,
       %(as_of_date)s AS as_of_date
FROM total_track_streams_for_date
ON CONFLICT DO NOTHING;