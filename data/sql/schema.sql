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
    relationship_type TEXT NOT NULL
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

CREATE TABLE IF NOT EXISTS mb_recording_credit (
    id SERIAL PRIMARY KEY,
    recording_mbid TEXT NOT NULL,
    artist_mbid TEXT NOT NULL,
    credit_type TEXT,
    credit_details TEXT,
    UNIQUE(recording_mbid, artist_mbid, credit_type)
);

CREATE TABLE IF NOT EXISTS mb_recording (
    id SERIAL PRIMARY KEY,
    recording_mbid TEXT NOT NULL UNIQUE,
    recording_title TEXT NOT NULL,
    recording_language TEXT
);

CREATE TABLE IF NOT EXISTS mb_unfetchable_isrc (
    isrc TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS mb_unmatchable_artist (
    artist_uri TEXT NOT NULL UNIQUE
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
    track_position TEXT,
    track_title TEXT,
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