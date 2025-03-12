DELETE FROM album
WHERE uri NOT IN (
    SELECT DISTINCT album_uri
    FROM track
);