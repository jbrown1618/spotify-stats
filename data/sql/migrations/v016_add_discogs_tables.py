from data.sql.migrations.migration import Migration


create_discogs_tables = """
CREATE TABLE IF NOT EXISTS discogs_artist (
    discogs_artist_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    realname TEXT,
    profile TEXT,
    data_quality TEXT,
    resource_url TEXT,
    primary_image_url TEXT,
    urls JSONB,
    namevariations JSONB,
    members JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sp_artist_discogs_artist (
    spotify_artist_uri TEXT NOT NULL,
    discogs_artist_id BIGINT NOT NULL,
    confidence NUMERIC,
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
    member_name TEXT NOT NULL,
    active BOOLEAN,
    resource_url TEXT,
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
    main_release_id BIGINT,
    data_quality TEXT,
    resource_url TEXT,
    genres JSONB,
    styles JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS discogs_release (
    discogs_release_id BIGINT PRIMARY KEY,
    discogs_master_id BIGINT,
    title TEXT NOT NULL,
    year INT,
    country TEXT,
    released TEXT,
    data_quality TEXT,
    resource_url TEXT,
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
    confidence NUMERIC,
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
    duration TEXT,
    duration_seconds INT,
    track_type TEXT,
    UNIQUE(discogs_master_id, position, title)
);
CREATE INDEX IF NOT EXISTS i_discogs_track_discogs_master_id
    ON discogs_track (discogs_master_id);

CREATE TABLE IF NOT EXISTS sp_track_discogs_track (
    spotify_track_uri TEXT NOT NULL,
    discogs_master_id BIGINT NOT NULL,
    discogs_track_position TEXT NOT NULL,
    discogs_track_title TEXT NOT NULL,
    confidence NUMERIC,
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

CREATE TABLE IF NOT EXISTS discogs_video (
    id BIGSERIAL PRIMARY KEY,
    discogs_master_id BIGINT NOT NULL,
    uri TEXT NOT NULL,
    title TEXT,
    description TEXT,
    duration_seconds INT,
    embed BOOLEAN,
    UNIQUE(discogs_master_id, uri)
);
CREATE INDEX IF NOT EXISTS i_discogs_video_discogs_master_id
    ON discogs_video (discogs_master_id);

CREATE TABLE IF NOT EXISTS discogs_unmatchable_artist (
    spotify_artist_uri TEXT NOT NULL UNIQUE,
    artist_name TEXT,
    reason TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS discogs_unmatchable_track (
    spotify_track_uri TEXT NOT NULL UNIQUE,
    track_name TEXT,
    reason TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


drop_discogs_tables = """
DROP TABLE IF EXISTS discogs_unmatchable_track;
DROP TABLE IF EXISTS discogs_unmatchable_artist;
DROP TABLE IF EXISTS discogs_video;
DROP TABLE IF EXISTS discogs_credit;
DROP TABLE IF EXISTS sp_track_discogs_track;
DROP TABLE IF EXISTS discogs_track;
DROP TABLE IF EXISTS sp_album_discogs_master;
DROP TABLE IF EXISTS discogs_release;
DROP TABLE IF EXISTS discogs_master;
DROP TABLE IF EXISTS discogs_artist_membership;
DROP TABLE IF EXISTS sp_artist_discogs_artist;
DROP TABLE IF EXISTS discogs_artist;
"""


class AddDiscogsTables(Migration):
    def __init__(self):
        super().__init__("v16")

    def migrate(self, cursor):
        cursor.execute(create_discogs_tables)

    def reverse(self, cursor):
        cursor.execute(drop_discogs_tables)


if __name__ == '__main__':
    AddDiscogsTables().perform_migration()
