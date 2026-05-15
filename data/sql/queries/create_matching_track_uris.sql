DROP TABLE IF EXISTS matching_track_uris;

CREATE TEMPORARY TABLE matching_track_uris AS
SELECT DISTINCT t.uri AS track_uri
FROM track t
    INNER JOIN playlist_track pt ON pt.track_uri = t.uri
    INNER JOIN album al ON al.uri = t.album_uri
    INNER JOIN track_artist ta ON ta.track_uri = t.uri
    INNER JOIN artist a ON a.uri = ta.artist_uri
    LEFT JOIN artist_genre ag ON ag.artist_uri = a.uri
    LEFT JOIN record_label rl ON rl.album_uri = t.album_uri
    LEFT JOIN sp_track_mb_recording stmr ON stmr.spotify_track_uri = t.uri
    LEFT JOIN mb_recording_credit rc ON rc.recording_mbid = stmr.recording_mbid
    LEFT JOIN (
        SELECT s.track_uri, COUNT(*) AS stream_count
        FROM track_stream s
        WHERE 
            (:wrapped_start_date IS NULL OR :wrapped_start_date <= s.played_at)
            AND 
            (:wrapped_end_date IS NULL OR :wrapped_end_date >= s.played_at)
        GROUP BY s.track_uri
    ) sc ON sc.track_uri = t.uri
WHERE
    (:filter_tracks = FALSE OR t.uri IN :track_uris)
    AND
    (:liked = FALSE OR t.uri IN (SELECT track_uri FROM liked_track))
    AND
    (:filter_playlists = FALSE OR pt.playlist_uri IN :playlist_uris)
    AND
    (:filter_artists = FALSE OR a.uri IN :artist_uris)
    AND
    (:filter_albums = FALSE OR al.uri IN :album_uris)
    AND
    (:filter_labels = FALSE OR rl.standardized_label IN (:labels))
    AND
    (:filter_genres = FALSE OR ag.genre IN (:genres))
    AND
    (:filter_producers = FALSE OR rc.artist_mbid IN (:producers))
    AND
    ((:wrapped_start_date IS NULL AND :wrapped_end_date IS NULL) OR sc.stream_count IS NOT NULL)
    AND
    (:filter_years = FALSE OR (
        CASE
        WHEN LENGTH(al.release_date) = 10
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM-DD'))
        WHEN LENGTH(al.release_date) = 7
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM'))
        WHEN LENGTH(al.release_date) = 4
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY'))
        ELSE 0
        END
        ) IN :years
    );
