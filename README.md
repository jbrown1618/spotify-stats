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

## Start the server

```bash
script/server
```

And navigate to `http://localhost:5000`

## Start the server with live client reloading

In two separate terminals, run:

```bash
script/server
```

```bash
script/client-dev
```

And navigate to `http://localhost:5173`