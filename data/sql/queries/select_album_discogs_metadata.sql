WITH mapped_masters AS (
    SELECT DISTINCT discogs_master_id
    FROM sp_album_discogs_master
    WHERE spotify_album_uri = :album_uri
)
SELECT
    dm.discogs_master_id,
    dm.title,
    dm.year,
    ARRAY(
        SELECT dmg.genre
        FROM discogs_master_genre dmg
        WHERE dmg.discogs_master_id = dm.discogs_master_id
            AND dmg.genre_source = 'genre'
        ORDER BY dmg.genre
    ) AS genres,
    ARRAY(
        SELECT dmg.genre
        FROM discogs_master_genre dmg
        WHERE dmg.discogs_master_id = dm.discogs_master_id
            AND dmg.genre_source = 'style'
        ORDER BY dmg.genre
    ) AS styles,
    ARRAY(
        SELECT DISTINCT dr.country
        FROM discogs_release dr
        WHERE dr.discogs_master_id = dm.discogs_master_id
            AND dr.country IS NOT NULL
        ORDER BY dr.country
    ) AS countries,
    ARRAY(
        SELECT DISTINCT label->>'name'
        FROM discogs_release dr
        CROSS JOIN JSONB_ARRAY_ELEMENTS(COALESCE(dr.labels, '[]'::JSONB)) AS label
        WHERE dr.discogs_master_id = dm.discogs_master_id
            AND label->>'name' IS NOT NULL
        ORDER BY label->>'name'
    ) AS labels,
    ARRAY(
        SELECT DISTINCT format_item->>'name'
        FROM discogs_release dr
        CROSS JOIN JSONB_ARRAY_ELEMENTS(
            COALESCE(dr.formats, '[]'::JSONB)
        ) AS format_item
        WHERE dr.discogs_master_id = dm.discogs_master_id
            AND format_item->>'name' IS NOT NULL
        ORDER BY format_item->>'name'
    ) AS formats
FROM mapped_masters mapping
INNER JOIN discogs_master dm
    ON dm.discogs_master_id = mapping.discogs_master_id
ORDER BY dm.year, dm.title;
