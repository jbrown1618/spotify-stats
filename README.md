# Spotify Stats

## Setup

```bash
# Clone the repo
git clone git@github.com:jbrown1618/spotify-stats.git
cd spotify-stats

# Set up the virtual environment
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r ./requirements.txt

# Set up environment variables
cp .env.sample .env
# Edit .env to include your Spotify credentials and desired output path

python ./main.py

# Exit the virtual environment
deactivate
```