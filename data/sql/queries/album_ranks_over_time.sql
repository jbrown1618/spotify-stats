SELECT album_uri, rank AS album_rank, stream_count AS album_stream_count, as_of_date
FROM album_rank
WHERE album_uri IN :album_uris
    AND (:from_date IS NULL OR as_of_date >= :from_date)
    AND (:to_date IS NULL OR as_of_date <= :to_date);