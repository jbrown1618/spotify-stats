drop table if exists tmp_album_stream_counts;

create temporary table tmp_album_stream_counts as
select t.album_uri, SUM(h.stream_count) as stream_count
from listening_history h
inner join listening_period p
    on h.listening_period_id = p.id
inner join track t
    on t.uri = h.track_uri
where 
    (:wrapped_start_date is NULL or :wrapped_start_date <= p.to_time)
    and 
    (:wrapped_end_date is NULL or :wrapped_end_date >= p.from_time)
group by t.album_uri;

select 
    al.uri as album_uri,
    al.name as album_name,
    al.short_name as album_short_name,
    al.album_type,
    al.label as album_label,
    al.popularity as album_popularity,
    al.release_date as album_release_date,
    al.image_url as album_image_url,
    sc.stream_count as album_stream_count,
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
from album al
    inner join track t on t.album_uri = al.uri
    left join album_rank alr
        on alr.album_uri = al.uri
        and as_of_date = (select max(as_of_date) from album_rank)
    left join tmp_album_stream_counts sc on sc.album_uri = al.uri
where (:filter_tracks = false or t.uri in :track_uris)
group by 
    al.uri,
    al.name,
    al.short_name,
    al.album_type,
    al.label,
    al.popularity,
    al.release_date,
    al.image_url,
    sc.stream_count

order by sc.stream_count desc nulls last;