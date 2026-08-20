WITH producer_credits AS (
    SELECT *
    FROM unified_track_credit
    WHERE producer_key = :producer_key
),
musicbrainz_ids AS (
    SELECT DISTINCT UNNEST(musicbrainz_artist_ids) AS artist_mbid
    FROM producer_credits
),
discogs_ids AS (
    SELECT DISTINCT UNNEST(discogs_artist_ids) AS discogs_artist_id
    FROM producer_credits
)
SELECT
    pc.producer_key,
    (ARRAY_AGG(
        pc.producer_name
        ORDER BY pc.producer_name IS NULL, pc.artist_uri IS NULL, pc.producer_name
    ))[1] AS producer_name,
    (ARRAY_REMOVE(ARRAY_AGG(DISTINCT pc.artist_uri), NULL))[1] AS artist_uri,
    (ARRAY_REMOVE(ARRAY_AGG(DISTINCT pc.artist_image_url), NULL))[1]
        AS artist_image_url,
    ARRAY_AGG(DISTINCT pc.credit_type ORDER BY pc.credit_type) AS credit_types,
    ARRAY(
        SELECT DISTINCT source
        FROM producer_credits source_credit
        CROSS JOIN UNNEST(source_credit.sources) AS source_value(source)
        ORDER BY source
    ) AS sources,
    COUNT(DISTINCT pc.track_uri) AS track_count,
    COUNT(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN pc.track_uri END)
        AS liked_track_count,
    COALESCE((
        SELECT JSONB_AGG(
            JSONB_BUILD_OBJECT(
                'artist_mbid', mb.artist_mbid,
                'name', mb.artist_mb_name,
                'sort_name', mb.artist_sort_name,
                'disambiguation', mb.artist_disambiguation,
                'type', mb.artist_type,
                'area', mb.artist_area,
                'birthplace', mb.artist_birthplace,
                'start_date', mb.artist_start_date,
                'end_date', mb.artist_end_date,
                'gender', mb.artist_gender,
                'aliases', COALESCE((
                    SELECT JSONB_AGG(
                        mba.alias_name
                        ORDER BY mba.primary_for_locale DESC, mba.alias_name
                    )
                    FROM mb_artist_alias mba
                    WHERE mba.artist_mbid = mb.artist_mbid
                ), '[]'::JSONB)
            )
            ORDER BY mb.artist_mb_name
        )
        FROM mb_artist mb
        INNER JOIN musicbrainz_ids mbi ON mbi.artist_mbid = mb.artist_mbid
    ), '[]'::JSONB) AS musicbrainz_artists,
    COALESCE((
        SELECT JSONB_AGG(
            JSONB_BUILD_OBJECT(
                'discogs_artist_id', da.discogs_artist_id,
                'name', da.name,
                'realname', da.realname,
                'profile', da.profile,
                'primary_image_url', da.primary_image_url,
                'namevariations', COALESCE(da.namevariations, '[]'::JSONB)
            )
            ORDER BY da.name
        )
        FROM discogs_artist da
        INNER JOIN discogs_ids di
            ON di.discogs_artist_id = da.discogs_artist_id
    ), '[]'::JSONB) AS discogs_artists
FROM producer_credits pc
LEFT JOIN liked_track lt ON lt.track_uri = pc.track_uri
GROUP BY pc.producer_key;
