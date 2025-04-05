SELECT
    ag.genre, 
    count(ta.track_uri) as genre_track_count,
    (
        SELECT COUNT(it.uri)
        FROM track it
            INNER JOIN track_artist ita ON ita.track_uri = it.uri
            INNER JOIN artist_genre iag ON iag.artist_uri = ita.artist_uri
        WHERE iag.genre = ag.genre
    ) as genre_total_track_count,
    count(lt.track_uri) as genre_liked_track_count,
    (
        SELECT COUNT(it.uri)
        FROM track it
            INNER JOIN liked_track ilt ON ilt.track_uri = it.uri
            INNER JOIN track_artist ita ON ita.track_uri = it.uri
            INNER JOIN artist_genre iag ON iag.artist_uri = ita.artist_uri
        WHERE iag.genre = ag.genre
    ) as genre_total_liked_track_count
FROM artist_genre ag
    INNER JOIN track_artist ta ON ag.artist_uri = ta.artist_uri
    LEFT JOIN liked_track lt ON ta.track_uri = lt.track_uri
WHERE ta.track_uri in %(track_uris)s
GROUP BY ag.genre;