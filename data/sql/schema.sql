CREATE TABLE IF NOT EXISTS version (
    id SERIAL PRIMARY KEY,
    version TEXT NOT NULL,
    timestamp timestamp default current_timestamp  
);

CREATE TABLE IF NOT EXISTS job (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    arguments TEXT NOT NULL,
    status TEXT DEFAULT 'QUEUED',
    error TEXT,
    summary JSONB NOT NULL DEFAULT '{}'::JSONB,
    queue_time timestamp DEFAULT current_timestamp,
    start_time timestamp,
    end_time timestamp,
);
CREATE INDEX IF NOT EXISTS i_job_status_queue_time ON job (status, queue_time);

CREATE TABLE IF NOT EXISTS album (
    id SERIAL PRIMARY KEY,
    uri TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    short_name TEXT DEFAULT '',
    album_type TEXT,
    label TEXT,
    popularity INT,
    total_tracks INT,
    release_date TEXT,
    image_url TEXT
);
CREATE INDEX IF NOT EXISTS i_album_uri ON album (uri);

CREATE TABLE IF NOT EXISTS record_label (
    id SERIAL PRIMARY KEY,
    album_uri TEXT NOT NULL,
    standardized_label TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS i_record_label_album_uri ON record_label (album_uri);

CREATE TABLE IF NOT EXISTS artist (
    id SERIAL PRIMARY KEY,
    uri TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    popularity INT,
    followers INT,
    image_url TEXT
);
CREATE INDEX IF NOT EXISTS i_artist_uri ON artist (uri);

CREATE TABLE IF NOT EXISTS track (
    id SERIAL PRIMARY KEY,
    uri TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    short_name TEXT DEFAULT '',
    popularity INT,
    explicit BOOLEAN,
    duration_ms INT,
    album_uri TEXT,
    isrc TEXT
);
CREATE INDEX IF NOT EXISTS i_track_uri ON track (uri);
CREATE INDEX IF NOT EXISTS i_track_album_uri ON track (album_uri);

CREATE TABLE IF NOT EXISTS playlist (
    id SERIAL PRIMARY KEY,
    uri TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    collaborative BOOLEAN,
    public BOOLEAN,
    image_url TEXT,
    owner TEXT
);
CREATE INDEX IF NOT EXISTS i_playlist_uri ON playlist (uri);

CREATE TABLE IF NOT EXISTS liked_track (
    track_uri TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS i_liked_track_track_uri ON liked_track (track_uri);

CREATE TABLE IF NOT EXISTS album_artist (
    album_uri TEXT NOT NULL,
    artist_uri TEXT NOT NULL,
    UNIQUE(album_uri, artist_uri)
);
CREATE INDEX IF NOT EXISTS i_album_artist_join ON album_artist (album_uri, artist_uri);

CREATE TABLE IF NOT EXISTS artist_genre (
    artist_uri TEXT NOT NULL,
    genre TEXT NOT NULL,
    UNIQUE(artist_uri, genre)
);
CREATE INDEX IF NOT EXISTS i_artist_genre_join ON artist_genre (artist_uri, genre);
CREATE INDEX IF NOT EXISTS i_artist_genre_genre ON artist_genre (genre);

CREATE TABLE IF NOT EXISTS playlist_track (
    playlist_uri TEXT NOT NULL,
    track_uri TEXT NOT NULL,
    UNIQUE(playlist_uri, track_uri)
);
CREATE INDEX IF NOT EXISTS i_playlist_track_join ON playlist_track (playlist_uri, track_uri);

CREATE TABLE IF NOT EXISTS track_artist (
    track_uri TEXT NOT NULL,
    artist_uri TEXT NOT NULL,
    artist_index INT NOT NULL,
    UNIQUE(track_uri, artist_uri)
);
CREATE INDEX IF NOT EXISTS i_track_artist_join ON track_artist (track_uri, artist_uri);
CREATE INDEX IF NOT EXISTS i_track_artist_joinIndex ON track_artist (track_uri, artist_uri, artist_index);

CREATE TABLE IF NOT EXISTS track_stream (
    id BIGSERIAL PRIMARY KEY,
    track_uri TEXT NOT NULL,
    played_at TIMESTAMP NOT NULL,
    UNIQUE(track_uri, played_at)
);
CREATE INDEX IF NOT EXISTS i_track_stream_track_uri ON track_stream (track_uri);
CREATE INDEX IF NOT EXISTS i_track_stream_played_at ON track_stream (played_at);

CREATE TABLE IF NOT EXISTS mb_artist_relationship (
    id SERIAL PRIMARY KEY,
    artist_mbid TEXT NOT NULL,
    other_mbid TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    UNIQUE(artist_mbid, other_mbid, relationship_type)
);

CREATE TABLE IF NOT EXISTS mb_artist (
    id SERIAL PRIMARY KEY,
    artist_mbid TEXT NOT NULL UNIQUE,
    artist_mb_name TEXT,
    artist_sort_name TEXT,
    artist_disambiguation TEXT,
    artist_type TEXT,
    artist_area TEXT,
    artist_birthplace TEXT,
    artist_start_date TEXT,
    artist_end_date TEXT,
    artist_gender TEXT
);

CREATE TABLE IF NOT EXISTS mb_artist_alias (
    artist_mbid TEXT NOT NULL,
    alias_name TEXT NOT NULL,
    sort_name TEXT NOT NULL DEFAULT '',
    locale TEXT NOT NULL DEFAULT '',
    alias_type TEXT NOT NULL DEFAULT '',
    primary_for_locale BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (artist_mbid, alias_name, sort_name, locale, alias_type)
);
CREATE INDEX IF NOT EXISTS i_mb_artist_alias_artist_mbid ON mb_artist_alias (artist_mbid);
CREATE INDEX IF NOT EXISTS i_mb_artist_alias_alias_name ON mb_artist_alias (LOWER(alias_name));

CREATE TABLE IF NOT EXISTS mb_recording_credit (
    id SERIAL PRIMARY KEY,
    recording_mbid TEXT NOT NULL,
    artist_mbid TEXT NOT NULL,
    raw_role TEXT NOT NULL,
    credit_type TEXT,
    credit_details TEXT NOT NULL DEFAULT '',
    UNIQUE(recording_mbid, artist_mbid, raw_role, credit_details)
);

CREATE TABLE IF NOT EXISTS mb_recording (
    id SERIAL PRIMARY KEY,
    recording_mbid TEXT NOT NULL UNIQUE,
    recording_title TEXT NOT NULL,
    recording_language TEXT
);

CREATE TABLE IF NOT EXISTS mb_unfetchable_isrc (
    isrc TEXT NOT NULL UNIQUE,
    reason TEXT,
    retry_after TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mb_unmatchable_artist (
    artist_uri TEXT NOT NULL UNIQUE,
    artist_name TEXT,
    reason TEXT,
    retry_after TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sp_artist_mb_artist (
    spotify_artist_uri TEXT NOT NULL,
    artist_mbid TEXT NOT NULL,
    UNIQUE(spotify_artist_uri, artist_mbid)
);

CREATE TABLE IF NOT EXISTS sp_track_mb_recording (
    spotify_track_uri TEXT NOT NULL,
    recording_mbid TEXT NOT NULL,
    UNIQUE(spotify_track_uri, recording_mbid)
);

CREATE TABLE IF NOT EXISTS discogs_artist (
    discogs_artist_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    realname TEXT,
    profile TEXT,
    primary_image_url TEXT,
    namevariations JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sp_artist_discogs_artist (
    spotify_artist_uri TEXT NOT NULL,
    discogs_artist_id BIGINT NOT NULL,
    match_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(spotify_artist_uri, discogs_artist_id)
);
CREATE INDEX IF NOT EXISTS i_sp_artist_discogs_artist_spotify_artist_uri
    ON sp_artist_discogs_artist (spotify_artist_uri);
CREATE INDEX IF NOT EXISTS i_sp_artist_discogs_artist_discogs_artist_id
    ON sp_artist_discogs_artist (discogs_artist_id);

CREATE TABLE IF NOT EXISTS discogs_artist_membership (
    group_discogs_artist_id BIGINT NOT NULL,
    member_discogs_artist_id BIGINT NOT NULL,
    active BOOLEAN,
    UNIQUE(group_discogs_artist_id, member_discogs_artist_id)
);
CREATE INDEX IF NOT EXISTS i_discogs_artist_membership_group_discogs_artist_id
    ON discogs_artist_membership (group_discogs_artist_id);
CREATE INDEX IF NOT EXISTS i_discogs_artist_membership_member_discogs_artist_id
    ON discogs_artist_membership (member_discogs_artist_id);

CREATE TABLE IF NOT EXISTS discogs_master (
    discogs_master_id BIGINT PRIMARY KEY,
    title TEXT NOT NULL,
    year INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS discogs_master_genre (
    discogs_master_id BIGINT NOT NULL,
    genre TEXT NOT NULL,
    genre_source TEXT NOT NULL,
    UNIQUE(discogs_master_id, genre, genre_source)
);
CREATE INDEX IF NOT EXISTS i_discogs_master_genre_discogs_master_id
    ON discogs_master_genre (discogs_master_id);
CREATE INDEX IF NOT EXISTS i_discogs_master_genre_genre
    ON discogs_master_genre (genre);

CREATE TABLE IF NOT EXISTS discogs_release (
    discogs_release_id BIGINT PRIMARY KEY,
    discogs_master_id BIGINT,
    title TEXT NOT NULL,
    year INT,
    country TEXT,
    released TEXT,
    labels JSONB,
    companies JSONB,
    formats JSONB,
    identifiers JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS i_discogs_release_discogs_master_id
    ON discogs_release (discogs_master_id);

CREATE TABLE IF NOT EXISTS sp_album_discogs_master (
    spotify_album_uri TEXT NOT NULL,
    discogs_master_id BIGINT NOT NULL,
    match_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(spotify_album_uri, discogs_master_id)
);
CREATE INDEX IF NOT EXISTS i_sp_album_discogs_master_spotify_album_uri
    ON sp_album_discogs_master (spotify_album_uri);
CREATE INDEX IF NOT EXISTS i_sp_album_discogs_master_discogs_master_id
    ON sp_album_discogs_master (discogs_master_id);

CREATE TABLE IF NOT EXISTS discogs_track (
    discogs_master_id BIGINT NOT NULL,
    position TEXT NOT NULL,
    title TEXT NOT NULL,
    UNIQUE(discogs_master_id, position, title)
);
CREATE INDEX IF NOT EXISTS i_discogs_track_discogs_master_id
    ON discogs_track (discogs_master_id);

CREATE TABLE IF NOT EXISTS sp_track_discogs_track (
    spotify_track_uri TEXT NOT NULL,
    discogs_master_id BIGINT NOT NULL,
    discogs_track_position TEXT NOT NULL,
    discogs_track_title TEXT NOT NULL,
    match_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(spotify_track_uri, discogs_master_id, discogs_track_position, discogs_track_title)
);
CREATE INDEX IF NOT EXISTS i_sp_track_discogs_track_spotify_track_uri
    ON sp_track_discogs_track (spotify_track_uri);
CREATE INDEX IF NOT EXISTS i_sp_track_discogs_track_discogs_master_id
    ON sp_track_discogs_track (discogs_master_id);

CREATE TABLE IF NOT EXISTS discogs_credit (
    id BIGSERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_id BIGINT NOT NULL,
    discogs_master_id BIGINT,
    track_position TEXT,
    track_title TEXT,
    discogs_artist_id BIGINT,
    artist_name TEXT NOT NULL,
    artist_anv TEXT,
    raw_role TEXT NOT NULL,
    credit_type TEXT NOT NULL,
    credit_details TEXT,
    UNIQUE(source_type, source_id, track_position, artist_name, raw_role)
);
CREATE INDEX IF NOT EXISTS i_discogs_credit_discogs_master_id
    ON discogs_credit (discogs_master_id);
CREATE INDEX IF NOT EXISTS i_discogs_credit_discogs_artist_id
    ON discogs_credit (discogs_artist_id);
CREATE INDEX IF NOT EXISTS i_discogs_credit_credit_type
    ON discogs_credit (credit_type);
CREATE UNIQUE INDEX IF NOT EXISTS i_discogs_credit_canonical_identity
    ON discogs_credit (
        discogs_master_id,
        track_position,
        COALESCE(discogs_artist_id, 0),
        artist_name,
        raw_role
    );

CREATE TABLE IF NOT EXISTS discogs_video (
    id BIGSERIAL PRIMARY KEY,
    discogs_master_id BIGINT NOT NULL,
    uri TEXT NOT NULL,
    title TEXT,
    description TEXT,
    duration_seconds INT,
    embed BOOLEAN,
    track_position TEXT NOT NULL,
    track_title TEXT NOT NULL,
    UNIQUE(discogs_master_id, uri)
);
CREATE INDEX IF NOT EXISTS i_discogs_video_discogs_master_id
    ON discogs_video (discogs_master_id);

CREATE TABLE IF NOT EXISTS discogs_unmatchable_artist (
    spotify_artist_uri TEXT NOT NULL UNIQUE,
    artist_name TEXT,
    reason TEXT NOT NULL,
    retry_after TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS discogs_unmatchable_track (
    spotify_track_uri TEXT NOT NULL UNIQUE,
    track_name TEXT,
    reason TEXT NOT NULL,
    retry_after TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW unified_track_credit AS
-- MusicBrainz aliases provide evidence that stage and legal names are one person.
WITH musicbrainz_name_variants AS (
    SELECT
        mb.artist_mbid,
        mb.artist_mb_name AS canonical_name,
        mb.artist_mb_name AS variant_name
    FROM mb_artist mb

    UNION

    SELECT
        mb.artist_mbid,
        mb.artist_mb_name AS canonical_name,
        mb.artist_sort_name AS variant_name
    FROM mb_artist mb

    UNION

    SELECT
        mb.artist_mbid,
        mb.artist_mb_name AS canonical_name,
        mba.alias_name AS variant_name
    FROM mb_artist mb
        INNER JOIN mb_artist_alias mba ON mba.artist_mbid = mb.artist_mbid
),
normalized_musicbrainz_names AS (
    SELECT
        artist_mbid,
        canonical_name,
        LOWER(
            REGEXP_REPLACE(
                REPLACE(
                    REGEXP_REPLACE(
                        canonical_name,
                        '[[:space:]]*\([0-9]+\)$',
                        ''
                    ),
                    '&',
                    'and'
                ),
                '[^[:alnum:]]+',
                '',
                'g'
            )
        ) AS canonical_name_key,
        LOWER(
            REGEXP_REPLACE(
                REPLACE(
                    REGEXP_REPLACE(
                        variant_name,
                        '[[:space:]]*\([0-9]+\)$',
                        ''
                    ),
                    '&',
                    'and'
                ),
                '[^[:alnum:]]+',
                '',
                'g'
            )
        ) AS variant_name_key
    FROM musicbrainz_name_variants
    WHERE canonical_name IS NOT NULL AND variant_name IS NOT NULL
),
-- Ignore ambiguous aliases that MusicBrainz assigns to more than one artist.
unique_musicbrainz_names AS (
    SELECT
        variant_name_key,
        MIN(canonical_name_key) AS canonical_name_key,
        MIN(canonical_name) AS canonical_name
    FROM normalized_musicbrainz_names
    WHERE variant_name_key <> '' AND canonical_name_key <> ''
    GROUP BY variant_name_key
    HAVING COUNT(DISTINCT artist_mbid) = 1
),
-- Project both providers into the same columns before resolving identities.
source_credits AS (
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
        INNER JOIN mb_recording_credit rc ON rc.recording_mbid = stmr.recording_mbid
        INNER JOIN mb_artist mb ON mb.artist_mbid = rc.artist_mbid
        LEFT JOIN sp_artist_mb_artist sama ON sama.artist_mbid = mb.artist_mbid
        LEFT JOIN artist a ON a.uri = sama.spotify_artist_uri

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
        LEFT JOIN discogs_artist da ON da.discogs_artist_id = dc.discogs_artist_id
        LEFT JOIN sp_artist_discogs_artist sada
            ON sada.discogs_artist_id = dc.discogs_artist_id
        LEFT JOIN artist a ON a.uri = sada.spotify_artist_uri
),
normalized_source_credits AS (
    SELECT
        *,
        LOWER(
            REGEXP_REPLACE(
                REPLACE(
                    REGEXP_REPLACE(
                        canonical_artist_name,
                        '[[:space:]]*\([0-9]+\)$',
                        ''
                    ),
                    '&',
                    'and'
                ),
                '[^[:alnum:]]+',
                '',
                'g'
            )
        ) AS normalized_artist_name
    FROM source_credits
),
-- Build a stable source-neutral key used by filters and cross-source grouping.
identified_credits AS (
    SELECT
        nsc.*,
        COALESCE(umn.canonical_name, nsc.canonical_artist_name)
            AS resolved_artist_name,
        'name:' || COALESCE(
            -- Prefer the canonical name behind a unique MusicBrainz alias.
            umn.canonical_name_key,
            NULLIF(nsc.normalized_artist_name, ''),
            -- Keep nameless credits distinct by falling back to their source ID.
            nsc.source || ':' || COALESCE(
                nsc.artist_mbid,
                nsc.discogs_artist_id::TEXT,
                nsc.canonical_artist_name
            )
        ) AS producer_key
    FROM normalized_source_credits nsc
        LEFT JOIN unique_musicbrainz_names umn
            ON umn.variant_name_key = nsc.normalized_artist_name
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
            resolved_artist_name
            ORDER BY resolved_artist_name IS NULL, artist_uri IS NULL, source
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