SELECT
    utc.producer_key,
    (ARRAY_AGG(
        utc.producer_name
        ORDER BY utc.producer_name IS NULL, utc.artist_uri IS NULL, utc.producer_name
    ))[1] AS producer_name,
    (ARRAY_REMOVE(ARRAY_AGG(DISTINCT utc.artist_uri), NULL))[1] AS artist_uri,
    (ARRAY_REMOVE(ARRAY_AGG(DISTINCT utc.artist_image_url), NULL))[1]
        AS artist_image_url,
    ARRAY_AGG(DISTINCT utc.credit_type) AS credit_types,
    COUNT(DISTINCT utc.track_uri) AS track_count,
    COUNT(DISTINCT CASE WHEN lt.track_uri IS NOT NULL THEN utc.track_uri END)
        AS liked_track_count
FROM unified_track_credit utc
    LEFT JOIN liked_track lt ON utc.track_uri = lt.track_uri
WHERE utc.track_uri IN (SELECT track_uri FROM matching_track_uris)
    AND utc.credit_type IN (
        'songwriter',
        'lyricist',
        'producer',
        'arranger',
        'sound',
        'mastering',
        'audio director',
        'video director',
        'publishing'
    )
GROUP BY utc.producer_key
ORDER BY track_count DESC, artist_image_url NULLS LAST;