SELECT artist_uri, rank as artist_rank, stream_count as artist_stream_count, as_of_date
FROM artist_rank
WHERE as_of_date = (
    SELECT MAX(as_of_date) FROM artist_rank
)
AND artist_uri IN :artist_uris;