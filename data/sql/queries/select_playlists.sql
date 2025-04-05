select
    p.uri as playlist_uri,
    p.name as playlist_name,
    p.collaborative as playlist_collaborative,
    p.public as playlist_public,
    p.image_url as playlist_image_url,
    p.owner as playlist_owner,
    (
        SELECT count(pt.track_uri)
        FROM playlist_track pt
        WHERE playlist_uri = p.uri
            AND (:filter_tracks = false or pt.track_uri in :track_uris)
    ) as playlist_track_count,
    (
        select count(track_uri)
        from playlist_track
        where playlist_uri = p.uri
    ) as playlist_total_track_count,
    (
        SELECT count(pt.track_uri)
        FROM playlist_track pt
            INNER JOIN liked_track lt ON lt.track_uri = pt.track_uri
        WHERE playlist_uri = p.uri
            AND (:filter_tracks = false or pt.track_uri in :track_uris)
    ) as playlist_liked_track_count,
    (
        select count(ipt.track_uri)
        from playlist_track ipt
        inner join liked_track lt on lt.track_uri = ipt.track_uri
        where playlist_uri = p.uri
    ) as playlist_total_liked_track_count
from playlist p
    inner join playlist_track pt on pt.playlist_uri = p.uri
where
    (:filter_tracks = false or pt.track_uri in :track_uris)
group by
    p.uri,
    p.name,
    p.collaborative,
    p.public,
    p.image_url,
    p.owner;