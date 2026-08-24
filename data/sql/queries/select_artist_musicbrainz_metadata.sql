SELECT
    mb.artist_mbid,
    mb.artist_mb_name AS name,
    mb.artist_sort_name AS sort_name,
    mb.artist_disambiguation AS disambiguation,
    mb.artist_type AS type,
    mb.artist_area AS area,
    mb.artist_birthplace AS birthplace,
    mb.artist_start_date AS start_date,
    mb.artist_end_date AS end_date,
    mb.artist_gender AS gender,
    ARRAY(
        SELECT DISTINCT mba.alias_name
        FROM mb_artist_alias mba
        WHERE mba.artist_mbid = mb.artist_mbid
        ORDER BY mba.alias_name
    ) AS aliases
FROM sp_artist_mb_artist mapping
INNER JOIN mb_artist mb ON mb.artist_mbid = mapping.artist_mbid
WHERE mapping.spotify_artist_uri = :artist_uri
ORDER BY mb.artist_mb_name;
