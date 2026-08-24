from data.sql.migrations.migration import Migration


create_unified_track_credits = """
CREATE OR REPLACE VIEW unified_track_credit AS
-- Project both providers into the same columns before resolving identities.
WITH source_credits AS (
    SELECT
        stmr.spotify_track_uri AS track_uri,
        rc.credit_type,
        rc.credit_details,
        rc.raw_role,
        -- Prefer Spotify metadata when this MusicBrainz artist is mapped.
        COALESCE(a.name, mb.artist_mb_name) AS canonical_artist_name,
        a.uri AS artist_uri,
        a.image_url AS artist_image_url,
        mb.artist_mbid,
        NULL::BIGINT AS discogs_artist_id,
        'musicbrainz'::TEXT AS source
    FROM sp_track_mb_recording stmr
        INNER JOIN mb_recording_credit rc
            ON rc.recording_mbid = stmr.recording_mbid
        INNER JOIN mb_artist mb
            ON mb.artist_mbid = rc.artist_mbid
        LEFT JOIN sp_artist_mb_artist sama
            ON sama.artist_mbid = mb.artist_mbid
        LEFT JOIN artist a
            ON a.uri = sama.spotify_artist_uri

    -- Keep all source rows here so the final grouping can preserve provenance.
    UNION ALL

    SELECT
        stdt.spotify_track_uri AS track_uri,
        dc.credit_type,
        dc.credit_details,
        dc.raw_role,
        -- Prefer Spotify, then the canonical Discogs artist, then credit text.
        COALESCE(a.name, da.name, dc.artist_name) AS canonical_artist_name,
        a.uri AS artist_uri,
        a.image_url AS artist_image_url,
        NULL::TEXT AS artist_mbid,
        dc.discogs_artist_id,
        'discogs'::TEXT AS source
    FROM sp_track_discogs_track stdt
        -- A Discogs credit belongs to the matched track at this master position.
        INNER JOIN discogs_credit dc
            ON dc.discogs_master_id = stdt.discogs_master_id
            AND dc.track_position = stdt.discogs_track_position
        LEFT JOIN discogs_artist da
            ON da.discogs_artist_id = dc.discogs_artist_id
        LEFT JOIN sp_artist_discogs_artist sada
            ON sada.discogs_artist_id = dc.discogs_artist_id
        LEFT JOIN artist a
            ON a.uri = sada.spotify_artist_uri
),
-- Build a stable source-neutral key used by filters and cross-source grouping.
identified_credits AS (
    SELECT
        *,
        'name:' || COALESCE(
            -- Normalize common catalog differences before comparing names.
            NULLIF(
                LOWER(
                    REGEXP_REPLACE(
                        REPLACE(
                            REGEXP_REPLACE(
                                canonical_artist_name,
                                '[[:space:]]*\\([0-9]+\\)$',
                                ''
                            ),
                            '&',
                            'and'
                        ),
                        '[^[:alnum:]]+',
                        '',
                        'g'
                    )
                ),
                ''
            ),
            -- Keep nameless credits distinct by falling back to their source ID.
            source || ':' || COALESCE(
                artist_mbid,
                discogs_artist_id::TEXT,
                canonical_artist_name
            )
        ) AS producer_key
    FROM source_credits
)
-- Collapse duplicate evidence to one row per track, person, and credit type.
SELECT
    track_uri,
    producer_key,
    credit_type,
    -- Retain distinct roles, details, provider IDs, and source provenance.
    STRING_AGG(DISTINCT NULLIF(credit_details, ''), '; ') AS credit_details,
    STRING_AGG(DISTINCT raw_role, '; ') AS raw_roles,
    COALESCE(
        (ARRAY_AGG(
            canonical_artist_name
            ORDER BY canonical_artist_name IS NULL, artist_uri IS NULL, source
        ))[1],
        'Unknown artist'
    ) AS producer_name,
    (ARRAY_REMOVE(ARRAY_AGG(DISTINCT artist_uri), NULL))[1] AS artist_uri,
    (ARRAY_REMOVE(ARRAY_AGG(DISTINCT artist_image_url), NULL))[1]
        AS artist_image_url,
    ARRAY_REMOVE(ARRAY_AGG(DISTINCT artist_mbid), NULL)
        AS musicbrainz_artist_ids,
    ARRAY_REMOVE(ARRAY_AGG(DISTINCT discogs_artist_id), NULL)
        AS discogs_artist_ids,
    ARRAY_AGG(DISTINCT source ORDER BY source) AS sources
FROM identified_credits
GROUP BY track_uri, producer_key, credit_type;
"""


drop_unified_track_credits = """
DROP VIEW IF EXISTS unified_track_credit;
"""


class AddUnifiedTrackCredits(Migration):
    def __init__(self):
        super().__init__("v21")

    def migrate(self, cursor):
        cursor.execute(create_unified_track_credits)

    def reverse(self, cursor):
        cursor.execute(drop_unified_track_credits)


if __name__ == "__main__":
    AddUnifiedTrackCredits().perform_migration()
