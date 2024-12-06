CREATE TABLE IF NOT EXISTS version (
    id SERIAL PRIMARY KEY,
    version TEXT NOT NULL,
    timestamp timestamp default current_timestamp  
);

CREATE TABLE IF NOT EXISTS album (
    id SERIAL PRIMARY KEY,
    uri TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    album_type TEXT,
    label TEXT,
    popularity INT,
    total_tracks INT,
    release_date TEXT,
    image_url TEXT
);

CREATE TABLE IF NOT EXISTS artist (
    id SERIAL PRIMARY KEY,
    uri TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    popularity INT,
    followers INT,
    image_url TEXT
);

CREATE TABLE IF NOT EXISTS track (
    id SERIAL PRIMARY KEY,
    uri TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    popularity INT,
    explicit BOOLEAN,
    duration_ms INT,
    album_uri TEXT,
    isrc TEXT
);

CREATE TABLE IF NOT EXISTS playlist (
    id SERIAL PRIMARY KEY,
    uri TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    collaborative BOOLEAN,
    public BOOLEAN,
    image_url TEXT,
    owner TEXT
);

CREATE TABLE IF NOT EXISTS liked_track (
    track_uri TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS top_track (
    id SERIAL PRIMARY KEY,
    track_uri TEXT NOT NULL,
    term TEXT NOT NULL,
    index INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (index, term, as_of_date)
);

CREATE TABLE IF NOT EXISTS top_artist (
    id SERIAL PRIMARY KEY,
    artist_uri TEXT NOT NULL,
    term TEXT NOT NULL,
    index INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (index, term, as_of_date)
);

CREATE TABLE IF NOT EXISTS track_ranks (
    id SERIAL PRIMARY KEY,
    track_uri TEXT NOT NULL,
    rank INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (rank, as_of_date)
);

CREATE TABLE IF NOT EXISTS artist_ranks (
    id SERIAL PRIMARY KEY,
    artist_uri TEXT NOT NULL,
    rank INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (rank, as_of_date)
);

CREATE TABLE IF NOT EXISTS album_ranks (
    id SERIAL PRIMARY KEY,
    album_uri TEXT NOT NULL,
    rank INT NOT NULL,
    as_of_date DATE NOT NULL,
    UNIQUE (rank, as_of_date)
);

CREATE TABLE IF NOT EXISTS album_artist (
    album_uri TEXT NOT NULL,
    artist_uri TEXT NOT NULL,
    UNIQUE(album_uri, artist_uri)
);

CREATE TABLE IF NOT EXISTS artist_genre (
    artist_uri TEXT NOT NULL,
    genre TEXT NOT NULL,
    UNIQUE(artist_uri, genre)
);

CREATE TABLE IF NOT EXISTS playlist_track (
    playlist_uri TEXT NOT NULL,
    track_uri TEXT NOT NULL,
    UNIQUE(playlist_uri, track_uri)
);

CREATE TABLE IF NOT EXISTS track_artist (
    track_uri TEXT NOT NULL,
    artist_uri TEXT NOT NULL,
    artist_index INT NOT NULL,
    UNIQUE(track_uri, artist_uri)
);

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