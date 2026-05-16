DROP TABLE IF EXISTS tmp_genre_track_counts;

CREATE TEMPORARY TABLE tmp_genre_track_counts AS
SELECT
    ag.genre,
    COUNT(DISTINCT ta.track_uri) AS total_track_count,
    COUNT(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN ta.track_uri END) AS total_liked_track_count
FROM artist_genre ag
    INNER JOIN track_artist ta ON ta.artist_uri = ag.artist_uri
    INNER JOIN playlist_track pt ON pt.track_uri = ta.track_uri
    LEFT JOIN liked_track lt ON lt.track_uri = ta.track_uri
GROUP BY ag.genre;

SELECT
    ag.genre, 
    count(DISTINCT ta.track_uri) as genre_track_count,
    COALESCE(gtc.total_track_count, 0) as genre_total_track_count,
    count(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN ta.track_uri END) as genre_liked_track_count,
    COALESCE(gtc.total_liked_track_count, 0) as genre_total_liked_track_count
FROM artist_genre ag
    INNER JOIN track_artist ta ON ag.artist_uri = ta.artist_uri
    LEFT JOIN liked_track lt ON ta.track_uri = lt.track_uri
    LEFT JOIN tmp_genre_track_counts gtc ON gtc.genre = ag.genre
WHERE ta.track_uri IN (SELECT track_uri FROM matching_track_uris)
GROUP BY ag.genre, gtc.total_track_count, gtc.total_liked_track_count;