WITH own_artists AS (
    SELECT artist_mbid
    FROM sp_artist_mb_artist
    WHERE spotify_artist_uri = :artist_uri
),
relationships AS (
    SELECT
        mar.other_mbid AS related_mbid,
        mar.relationship_type,
        'forward' AS relationship_direction
    FROM own_artists own
        INNER JOIN mb_artist_relationship mar
            ON mar.artist_mbid = own.artist_mbid

    UNION ALL

    SELECT
        mar.artist_mbid AS related_mbid,
        mar.relationship_type,
        'backward' AS relationship_direction
    FROM own_artists own
        INNER JOIN mb_artist_relationship mar
            ON mar.other_mbid = own.artist_mbid
)
SELECT
    related.artist_mbid,
    related.artist_mb_name,
    related.artist_sort_name,
    relationships.relationship_type,
    relationships.relationship_direction,
    spotify.uri AS artist_uri,
    spotify.name AS artist_name,
    spotify.image_url AS artist_image_url
FROM relationships
    INNER JOIN mb_artist related
        ON related.artist_mbid = relationships.related_mbid
    LEFT JOIN sp_artist_mb_artist mapping
        ON mapping.artist_mbid = related.artist_mbid
    LEFT JOIN artist spotify
        ON spotify.uri = mapping.spotify_artist_uri
ORDER BY
    relationships.relationship_type,
    relationships.relationship_direction,
    related.artist_sort_name,
    spotify.uri;
