SELECT artist_uri, rank as artist_rank, stream_count as artist_stream_count, as_of_date
FROM artist_rank
WHERE artist_uri IN :artist_uris
    AND (:from_date IS NULL OR as_of_date >= :from_date)
    AND (:to_date IS NULL OR as_of_date <= :to_date);