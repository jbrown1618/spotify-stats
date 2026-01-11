-- Find tracks that have streams but are not in any playlist
-- Uses UNION to dedupe track URIs from both tables first, then checks against playlists
WITH streamed_tracks AS (
    SELECT DISTINCT track_uri FROM track_stream
    UNION
    SELECT DISTINCT track_uri FROM listening_history
)
SELECT st.track_uri, t.name
FROM streamed_tracks st
INNER JOIN track t ON t.uri = st.track_uri
LEFT JOIN playlist_track pt ON pt.track_uri = st.track_uri
WHERE pt.track_uri IS NULL