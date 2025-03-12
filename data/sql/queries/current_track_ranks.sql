SELECT track_uri, rank as track_rank, stream_count as track_stream_count, as_of_date
FROM track_rank
WHERE as_of_date = (
    SELECT MAX(as_of_date) FROM track_rank
)
AND track_uri IN :track_uris;