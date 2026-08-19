WITH artist_credit_keys AS (
    SELECT DISTINCT producer_key
    FROM unified_track_credit
    WHERE artist_uri = :artist_uri
)
SELECT
    utc.producer_key,
    utc.credit_type,
    utc.credit_details,
    utc.raw_roles,
    utc.track_uri,
    t.name AS track_name,
    utc.sources
FROM unified_track_credit utc
    INNER JOIN artist_credit_keys ack ON ack.producer_key = utc.producer_key
    LEFT JOIN track t ON t.uri = utc.track_uri
WHERE utc.credit_type IN (
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
ORDER BY utc.credit_type, t.name;
