SELECT
    ag.genre, 
    count(ta.track_uri) as genre_track_count,
    count(lt.track_uri) as genre_liked_track_count
FROM artist_genre ag
    INNER JOIN track_artist ta ON ag.artist_uri = ta.artist_uri
    LEFT JOIN liked_track lt ON ta.track_uri = lt.track_uri
WHERE ta.track_uri in %(track_uris)s
GROUP BY ag.genre;