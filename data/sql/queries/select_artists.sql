select
    a.uri as artist_uri,
    a.name as artist_name,
    a.popularity as artist_popularity,
    a.followers as artist_followers,
    a.image_url as artist_image_url,
    ar.rank as artist_rank,
    ar.stream_count as artist_stream_count,
    (
        select count(track_uri) 
        from (
            select distinct ita.track_uri
            from track_artist ita 
            inner join liked_track ilt on ilt.track_uri = ita.track_uri
            where ita.artist_uri = a.uri
            and ita.track_uri in (
                select track_uri from playlist_track
            )
        )
    ) as artist_liked_track_count,
    (
        select count(track_uri) 
        from (
            select distinct ita.track_uri
            from track_artist ita 
            where ita.artist_uri = a.uri
            and ita.track_uri in (
                select track_uri from playlist_track
            )
        )
    ) as artist_track_count

from artist a
    inner join track_artist ta on ta.artist_uri = a.uri
    inner join playlist_track pt on ta.track_uri = pt.track_uri
    left join artist_rank ar on ar.artist_uri = a.uri and ar.as_of_date = (select max(as_of_date) from artist_rank)
    left join sp_artist_mb_artist sp_mb_a on sp_mb_a.spotify_artist_uri = a.uri
    left join mb_artist mba on mba.artist_mbid = sp_mb_a.artist_mbid
WHERE
    (:filter_artists = false or a.uri in :artist_uris)
    AND
    (:filter_tracks = false or ta.track_uri in :track_uris)
    AND
    (:filter_mbids = false or mba.artist_mbid in :mbids)
group by
    a.uri,
    a.name,
    a.popularity,
    a.followers,
    a.image_url,
    ar.rank,
    ar.stream_count

order by ar.rank asc nulls last;