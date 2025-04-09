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