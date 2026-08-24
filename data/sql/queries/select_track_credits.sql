SELECT
    producer_key,
    producer_name,
    credit_type,
    credit_details,
    raw_roles,
    artist_uri,
    artist_image_url,
    musicbrainz_artist_ids,
    discogs_artist_ids,
    sources
FROM unified_track_credit
WHERE track_uri = :track_uri
ORDER BY credit_type, producer_name;
