drop table if exists tmp_artist_stream_counts;

create temporary table tmp_artist_stream_counts as
select ta.artist_uri, SUM(h.stream_count) as stream_count
from listening_history h
inner join listening_period p
    on h.listening_period_id = p.id
inner join track_artist ta
    on ta.track_uri = h.track_uri
where 
    (:wrapped_start_date is NULL or :wrapped_start_date <= p.to_time)
    and 
    (:wrapped_end_date is NULL or :wrapped_end_date >= p.from_time)
group by ta.artist_uri;

select
    a.uri as artist_uri,
    a.name as artist_name,
    a.popularity as artist_popularity,
    a.followers as artist_followers,
    a.image_url as artist_image_url,
    sc.stream_count as artist_stream_count,
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
    ) as artist_total_liked_track_count,
    (
        select count(track_uri) 
        from (
            select distinct ita.track_uri
            from track_artist ita 
            inner join liked_track ilt on ilt.track_uri = ita.track_uri
            where ita.artist_uri = a.uri
            and (:filter_tracks = false or ita.track_uri in :track_uris)
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
    ) as artist_total_track_count,
    (
        select count(track_uri) 
        from (
            select distinct ita.track_uri
            from track_artist ita 
            where ita.artist_uri = a.uri
            and (:filter_tracks = false or ita.track_uri in :track_uris)
        )
    ) as artist_track_count

from artist a
    inner join track_artist ta on ta.artist_uri = a.uri
    inner join playlist_track pt on ta.track_uri = pt.track_uri
    left join sp_artist_mb_artist sp_mb_a on sp_mb_a.spotify_artist_uri = a.uri
    left join mb_artist mba on mba.artist_mbid = sp_mb_a.artist_mbid
    left join tmp_artist_stream_counts sc on sc.artist_uri = a.uri
WHERE
    (:filter_artists = false or a.uri in :artist_uris)
    AND
    (:filter_tracks = false or ta.track_uri in :track_uris)
    AND
    (:filter_mbids = false or mba.artist_mbid in :mbids)
    and
    ((:wrapped_start_date is NULL AND :wrapped_end_date is NULL) or sc.stream_count is not null)
group by
    a.uri,
    a.name,
    a.popularity,
    a.followers,
    a.image_url,
    sc.stream_count

order by sc.stream_count desc nulls last;