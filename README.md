# Spotify Stats

A React and Flask web app for exploring personal Spotify listening data stored in
PostgreSQL.

## Setup

Install Python 3, PostgreSQL, Node.js 20, and npm 10, then run:

```bash
git clone git@github.com:jbrown1618/spotify-stats.git
cd spotify-stats
script/setup
source venv/bin/activate
createdb spotifystats
python -m script.init_postgres
cd client && npm install && cd ..
```

Update `.env` with the local PostgreSQL credentials and Spotify API credentials.
For an existing database, run `script/db-migrate`; the Flask app also applies
outstanding migrations when it starts.

## Development

Run the backend and frontend in separate shells:

```bash
script/dev-server
```

```bash
script/dev-client
```

Open `http://localhost:5173`. Vite proxies API requests to Flask on port 5000.

## Demo data

Seed the local database with repeatable sample artists, albums, playlists, and
listening history for screenshots:

```bash
python -m script.seed_demo_data
```

By default, the script seeds 2025 and prints a URL for its Wrapped view. It only
adds or updates its own demo records; it does not clear existing listening data.
Use `--year` to choose another year. If `DATABASE_URL` is set, the script stops
unless `--allow-database-url` is passed; only use that option with a disposable
database.

## Jobs

Run the database-backed worker in one shell:

```bash
script/job-agent
```

Queue a job from another shell, optionally passing a JSON object as its second
argument:

```bash
python -m script.queue save_spotify_data
python -m script.queue save_listening_data
python -m script.queue save_musicbrainz_data '{"max_tracks": 1000}'
python -m script.queue save_discogs_data '{"max_tracks": 1000}'
```

MusicBrainz and Discogs use their default track limits when `max_tracks` is
omitted. An explicit `max_tracks` value overrides the default.

Spotify imports automatically queue record-label standardization and orphan-track
repair jobs.

## Spotify authorization cache

Set `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, and `SPOTIFY_REDIRECT_URI` in
`.env`, then generate or refresh the Spotipy cache:

```bash
script/spotify-cache > spotify-cache.json
```

If prompted, approve the Spotify authorization URL and paste the complete
redirected loopback URL containing `?code=...`. The redirect URI must exactly
match the URI configured in the Spotify Developer Dashboard. For deployment,
copy the generated JSON into the `SPOTIFY_CACHE` environment variable; the app
uses it to initialize the local `.cache` file.

## Mirror the production database

Pass a production PostgreSQL connection string to:

```bash
script/mirror-production-database "$PRODUCTION_DATABASE_URL"
```

The script archives the current local `spotifystats` database, recreates it, and
imports the production backup. It requires `psql`, `pg_dump`, and `pg_restore`.
