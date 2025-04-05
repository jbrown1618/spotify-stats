SELECT 
    i.album_release_year as release_year,
    COUNT(i.track_uri) as track_count,
    COUNT(i.track_liked) AS liked_track_count,
    (
        SELECT COUNT(it.uri)
        FROM track it 
            INNER JOIN album ial ON ial.uri = it.album_uri
        WHERE i.album_release_year = (
            case
            when length(ial.release_date) = 10
                then extract(year from to_date(ial.release_date, 'YYYY-MM-DD'))
            when length(ial.release_date) = 7
                then extract(year from to_date(ial.release_date, 'YYYY-MM'))
            when length(ial.release_date) = 4
                then extract(year from to_date(ial.release_date, 'YYYY'))
            else 0
            end
        )
    ) as total_track_count,
    (
        SELECT COUNT(it.uri)
        FROM track it 
            INNER JOIN liked_track ilt ON ilt.track_uri = it.uri
            INNER JOIN album ial ON ial.uri = it.album_uri
        WHERE i.album_release_year = (
            case
            when length(ial.release_date) = 10
                then extract(year from to_date(ial.release_date, 'YYYY-MM-DD'))
            when length(ial.release_date) = 7
                then extract(year from to_date(ial.release_date, 'YYYY-MM'))
            when length(ial.release_date) = 4
                then extract(year from to_date(ial.release_date, 'YYYY'))
            else 0
            end
        )
    ) as total_liked_track_count
FROM (
    SELECT 
        it.uri as track_uri,
        ilt.track_uri AS track_liked,
        (
            case
            when length(ial.release_date) = 10
                then extract(year from to_date(ial.release_date, 'YYYY-MM-DD'))
            when length(ial.release_date) = 7
                then extract(year from to_date(ial.release_date, 'YYYY-MM'))
            when length(ial.release_date) = 4
                then extract(year from to_date(ial.release_date, 'YYYY'))
            else 0
            end
        ) as album_release_year
    FROM album ial
    INNER JOIN track it ON it.album_uri = ial.uri
    LEFT JOIN liked_track ilt ON ilt.track_uri = it.uri
    WHERE it.uri IN %(track_uris)s
) i
GROUP BY i.album_release_year
