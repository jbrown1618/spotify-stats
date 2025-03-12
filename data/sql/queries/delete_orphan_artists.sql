DELETE FROM artist
WHERE uri NOT IN (
    SELECT DISTINCT artist_uri
    FROM track_artist
);