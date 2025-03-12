SELECT track_uri
FROM listening_history
WHERE track_uri NOT IN (
    SELECT uri FROM track
);