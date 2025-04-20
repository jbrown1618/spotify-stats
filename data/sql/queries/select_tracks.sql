select
    t.uri as track_uri,
    t.name as track_name,
    t.short_name as track_short_name,
    t.popularity as track_popularity,
    t.explicit as track_explicit,
    t.duration_ms as track_duration_ms,
    t.isrc as track_isrc,
    t.uri in (select track_uri from liked_track) as track_liked,
    (
        select SUM(h.stream_count)
        from listening_history h
        inner join listening_period p
            on p.id = h.listening_period_id
        where 
        (:wrapped_start_date is NULL or :wrapped_start_date <= p.to_time)
        and 
        (:wrapped_end_date is NULL or :wrapped_end_date >= p.from_time)
        and h.track_uri = t.uri

    ) as track_stream_count,

    al.uri as album_uri,
    al.name as album_name,
    al.short_name as album_short_name,
    al.album_type,
    al.label as album_label,
    al.popularity as album_popularity,
    al.release_date as album_release_date,
    al.image_url as album_image_url,
    (
        case
        when length(al.release_date) = 10
            then extract(year from to_date(al.release_date, 'YYYY-MM-DD'))
        when length(al.release_date) = 7
            then extract(year from to_date(al.release_date, 'YYYY-MM'))
        when length(al.release_date) = 4
            then extract(year from to_date(al.release_date, 'YYYY'))
        else 0
        end
    ) as album_release_year

from track t
    inner join playlist_track pt on pt.track_uri = t.uri
    inner join album al on al.uri = t.album_uri
    inner join track_artist ta on ta.track_uri = t.uri
    inner join artist a on a.uri = ta.artist_uri
    left join artist_genre ag on ag.artist_uri = a.uri
    left join record_label rl
        on rl.album_uri = t.album_uri
    left join sp_track_mb_recording stmr
        on stmr.spotify_track_uri = t.uri
    left join mb_recording_credit rc
        on rc.recording_mbid = stmr.recording_mbid
    left join listening_history h
        on h.track_uri = t.uri
    left join listening_period p
        on h.listening_period_id = p.id

where
    (:filter_tracks = false or t.uri in :track_uris)
    and
    (:liked = false or t.uri in (select track_uri from liked_track))
    and
    (:filter_playlists = false or pt.playlist_uri in :playlist_uris)
    and
    (:filter_artists = false or a.uri in :artist_uris)
    and
    (:filter_albums = false or al.uri in :album_uris)
    and
    (:filter_labels = false or rl.standardized_label in (:labels))
    and
    (:filter_genres = false or ag.genre in (:genres))
    and
    (:filter_producers = false or rc.artist_mbid in (:producers))
    and
    (:wrapped_start_date is NULL or t.uri in (
        select wh.track_uri
        from listening_history wh
        inner join listening_period wp on wp.id = wh.listening_period_id
        where :wrapped_start_date <= p.to_time
    ))
    and
    (:wrapped_start_date is NULL or t.uri in (
        select wh.track_uri
        from listening_history wh
        inner join listening_period wp on wp.id = wh.listening_period_id
        where :wrapped_end_date >= p.from_time
    ))
    and
    (:filter_years = false or (
        case
        when length(al.release_date) = 10
            then extract(year from to_date(al.release_date, 'YYYY-MM-DD'))
        when length(al.release_date) = 7
            then extract(year from to_date(al.release_date, 'YYYY-MM'))
        when length(al.release_date) = 4
            then extract(year from to_date(al.release_date, 'YYYY'))
        else 0
        end
        ) in :years
    )

group by
    t.uri,
    t.name,
    t.short_name,
    t.popularity,
    t.explicit,
    t.duration_ms,
    t.isrc,

    al.uri,
    al.name,
    al.short_name,
    al.album_type,
    al.label,
    al.popularity,
    al.release_date,
    al.image_url

order by track_stream_count desc nulls last;