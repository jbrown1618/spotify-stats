select
    t.uri as track_uri,
    t.name as track_name,
    t.short_name as track_short_name,
    t.popularity as track_popularity,
    t.explicit as track_explicit,
    t.duration_ms as track_duration_ms,
    t.isrc as track_isrc,
    t.uri in (select track_uri from liked_track) as track_liked,
    tr.rank as track_rank,
    coalesce(tr.stream_count, 0) as track_stream_count,

    al.uri as album_uri,
    al.name as album_name,
    al.short_name as album_short_name,
    al.album_type,
    al.label as album_label,
    al.popularity as album_popularity,
    al.release_date as album_release_date,
    al.image_url as album_image_url,
    alr.rank as album_rank,
    alr.stream_count as album_stream_count,
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
    left join track_rank tr
        on tr.track_uri = t.uri
        and tr.as_of_date = (select max(as_of_date) from track_rank)
    left join album_rank alr
        on alr.album_uri = al.uri
        and alr.as_of_date = (select max(as_of_date) from album_rank)
    left join artist_rank ar
        on ar.artist_uri = a.uri
        and ar.as_of_date = (select max(as_of_date) from artist_rank)
    left join record_label rl
        on rl.album_uri = t.album_uri
    left join sp_track_mb_recording stmr
        on stmr.spotify_track_uri = t.uri
    left join mb_recording_credit rc
        on rc.recording_mbid = stmr.recording_mbid

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
    tr.rank,
    tr.stream_count,

    al.uri,
    al.name,
    al.short_name,
    al.album_type,
    al.label,
    al.popularity,
    al.release_date,
    al.image_url,
    alr.rank,
    alr.stream_count

order by tr.rank asc nulls last;