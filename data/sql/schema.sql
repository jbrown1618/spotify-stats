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

CREATE TABLE IF NOT EXISTS track_rank (
    id BIGSERIAL PRIMARY KEY,
    track_uri TEXT NOT NULL,
    rank INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (rank, as_of_date),
    UNIQUE (track_uri, as_of_date)
);
CREATE INDEX IF NOT EXISTS i_track_rank_track_uri ON track_rank (track_uri);

CREATE TABLE IF NOT EXISTS artist_rank (
    id BIGSERIAL PRIMARY KEY,
    artist_uri TEXT NOT NULL,
    rank INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (rank, as_of_date),
    UNIQUE (artist_uri, as_of_date)
);
CREATE INDEX IF NOT EXISTS i_artist_rank_artist_uri ON artist_rank (artist_uri);

CREATE TABLE IF NOT EXISTS album_rank (
    id BIGSERIAL PRIMARY KEY,
    album_uri TEXT NOT NULL,
    rank INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (rank, as_of_date),
    UNIQUE (album_uri, as_of_date)
);
CREATE INDEX IF NOT EXISTS i_album_rank_album_uri ON album_rank (album_uri);

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

CREATE TABLE IF NOT EXISTS listening_period (
    id SERIAL PRIMARY KEY,
    from_time TIMESTAMP NOT NULL,
    to_time TIMESTAMP NOT NULL,
    UNIQUE (from_time, to_time)
);

CREATE TABLE IF NOT EXISTS listening_history (
    id SERIAL PRIMARY KEY,
    listening_period_id INTEGER REFERENCES listening_period (id),
    track_uri TEXT NOT NULL,
    stream_count INTEGER DEFAULT 0,
    UNIQUE(listening_period_id, track_uri)
);

CREATE TABLE IF NOT EXISTS stream (
    id BIGSERIAL PRIMARY KEY,
    track_uri TEXT NOT NULL,
    played_at TIMESTAMP NOT NULL,
    UNIQUE(track_uri, played_at)
);
CREATE INDEX IF NOT EXISTS i_stream_track_uri ON stream (track_uri);
CREATE INDEX IF NOT EXISTS i_stream_played_at ON stream (played_at);

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