SELECT
    p.uri AS playlist_uri,
    p.name AS playlist_name,
    p.collaborative AS playlist_collaborative,
    p.public AS playlist_public,
    p.image_url AS playlist_image_url,
    p.owner AS playlist_owner,
    (
        SELECT COUNT(pt.track_uri)
        FROM playlist_track pt
        WHERE playlist_uri = p.uri
            AND (:filter_tracks = FALSE OR pt.track_uri IN :track_uris)
    ) AS playlist_track_count,
    (
        SELECT COUNT(track_uri)
        FROM playlist_track
        WHERE playlist_uri = p.uri
    ) AS playlist_total_track_count,
    (
        SELECT COUNT(pt.track_uri)
        FROM playlist_track pt
            INNER JOIN liked_track lt ON lt.track_uri = pt.track_uri
        WHERE playlist_uri = p.uri
            AND (:filter_tracks = FALSE OR pt.track_uri IN :track_uris)
    ) AS playlist_liked_track_count,
    (
        SELECT COUNT(ipt.track_uri)
        FROM playlist_track ipt
        INNER JOIN liked_track lt ON lt.track_uri = ipt.track_uri
        WHERE playlist_uri = p.uri
    ) AS playlist_total_liked_track_count
FROM playlist p
    INNER JOIN playlist_track pt ON pt.playlist_uri = p.uri
WHERE
    (:filter_tracks = FALSE OR pt.track_uri IN :track_uris)
GROUP BY
    p.uri,
    p.name,
    p.collaborative,
    p.public,
    p.image_url,
    p.owner;