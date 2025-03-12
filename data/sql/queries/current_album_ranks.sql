SELECT album_uri, rank as album_rank, stream_count as album_stream_count, as_of_date
FROM album_rank
WHERE as_of_date = (
    SELECT MAX(as_of_date) FROM album_rank
)
AND album_uri IN :album_uris;