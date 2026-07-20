# Spotify Stats

## Setup

```bash
# Clone the repo
git clone git@github.com:jbrown1618/spotify-stats.git
cd spotify-stats

script/setup

# Edit .env to include your Spotify credentials and desired output path

python ./main.py

# Exit the virtual environment
deactivate
```

## Start the server with live client reloading

Run in separate shells:

```bash
script/dev-server
```

```bash
script/dev-client
```

And navigate to `http://localhost:5173`

## Refresh Spotify authorization cache

If Spotify authorization expires, run:

```bash
script/spotify-cache > spotify-cache.json
```

The script sends a Spotify request, runs the local authorization flow if needed,
and writes the updated Spotipy cache JSON to stdout. If prompted, open the
Spotify authorization URL, approve access, then paste the redirected loopback
URL containing `?code=...`. Copy the file contents into the `SPOTIFY_CACHE`
Heroku config var.

The Spotify app's redirect URI must exactly match `SPOTIFY_REDIRECT_URI` in
`.env`. The default is `http://127.0.0.1:8888`, which should be added to the
Spotify Developer Dashboard app settings.
