import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from utils.settings import spotify_cache, spotify_client_id, spotify_client_secret

def get_spotify_client() -> spotipy.Spotify:
    if not os.path.exists('.cache'):
        cache = spotify_cache()
        with open(".cache", "w") as f:
            f.write(cache)

    auth_manager = SpotifyOAuth(
        client_id=spotify_client_id(),
        client_secret=spotify_client_secret(),
        redirect_uri="http://localhost:3000/",
        open_browser=False,
        scope="user-library-read user-top-read user-read-recently-played playlist-read-collaborative"
    )

    sp = spotipy.Spotify(
        auth_manager=auth_manager,
        requests_timeout=10,
        retries=10
    )

    return sp