SELECT track_uri, rank as track_rank, stream_count as track_stream_count, as_of_date
FROM track_rank
WHERE track_uri IN :track_uris;