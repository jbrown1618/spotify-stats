DROP TABLE IF EXISTS tmp_stream_counts;

CREATE TEMPORARY TABLE tmp_stream_counts AS
SELECT h.track_uri, SUM(h.stream_count) AS stream_count
FROM listening_history h
INNER JOIN listening_period p
    ON h.listening_period_id = p.id
WHERE 
    (:wrapped_start_date IS NULL OR :wrapped_start_date <= p.to_time)
    AND 
    (:wrapped_end_date IS NULL OR :wrapped_end_date >= p.from_time)
GROUP BY h.track_uri;

SELECT
    t.uri AS track_uri,
    t.name AS track_name,
    t.short_name AS track_short_name,
    t.popularity AS track_popularity,
    t.explicit AS track_explicit,
    t.duration_ms AS track_duration_ms,
    t.isrc AS track_isrc,
    t.uri IN (SELECT track_uri FROM liked_track) AS track_liked,
    sc.stream_count AS track_stream_count,

    ARRAY_AGG(DISTINCT a.name) AS artist_names,

    al.uri AS album_uri,
    al.name AS album_name,
    al.short_name AS album_short_name,
    al.album_type,
    al.label AS album_label,
    al.popularity AS album_popularity,
    al.release_date AS album_release_date,
    al.image_url AS album_image_url,
    (
        CASE
        WHEN LENGTH(al.release_date) = 10
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM-DD'))
        WHEN LENGTH(al.release_date) = 7
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY-MM'))
        WHEN LENGTH(al.release_date) = 4
            THEN EXTRACT(YEAR FROM TO_DATE(al.release_date, 'YYYY'))
        ELSE 0
        END
    ) AS album_release_year

FROM track t
    INNER JOIN playlist_track pt ON pt.track_uri = t.uri
    INNER JOIN album al ON al.uri = t.album_uri
    INNER JOIN track_artist ta ON ta.track_uri = t.uri
    INNER JOIN artist a ON a.uri = ta.artist_uri
    LEFT JOIN artist_genre ag ON ag.artist_uri = a.uri
    LEFT JOIN record_label rl ON rl.album_uri = t.album_uri
    LEFT JOIN sp_track_mb_recording stmr ON stmr.spotify_track_uri = t.uri
    LEFT JOIN mb_recording_credit rc ON rc.recording_mbid = stmr.recording_mbid
    LEFT JOIN tmp_stream_counts sc ON sc.track_uri = t.uri

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
    )

GROUP BY
    t.uri,
    t.name,
    t.short_name,
    t.popularity,
    t.explicit,
    t.duration_ms,
    t.isrc,
    sc.stream_count,

    al.uri,
    al.name,
    al.short_name,
    al.album_type,
    al.label,
    al.popularity,
    al.release_date,
    al.image_url

ORDER BY track_stream_count DESC NULLS LAST;