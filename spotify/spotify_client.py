import os
import spotipy
from spotipy.oauth2 import CacheFileHandler, SpotifyOAuth, SpotifyOauthError

from utils.settings import spotify_cache, spotify_client_id, spotify_client_secret

spotify_cache_path = ".cache"


def ensure_spotify_cache_file():
    if not os.path.exists(spotify_cache_path):
        cache = spotify_cache()
        if cache is None:
            return
        with open(spotify_cache_path, "w") as f:
            f.write(cache)


def get_spotify_auth_manager() -> SpotifyOAuth:
    ensure_spotify_cache_file()
    auth_manager = SpotifyOAuth(
        client_id=spotify_client_id(),
        client_secret=spotify_client_secret(),
        redirect_uri="http://localhost:3000/",
        open_browser=False,
        scope="user-library-read user-top-read user-read-recently-played playlist-read-collaborative",
        cache_handler=CacheFileHandler(cache_path=spotify_cache_path),
    )
    return auth_manager


def get_spotify_client() -> spotipy.Spotify:
    auth_manager = get_spotify_auth_manager()

    sp = spotipy.Spotify(
        auth_manager=auth_manager,
        requests_timeout=10,
        retries=10
    )

    return sp


def spotify_auth_status() -> dict[str, str]:
    auth_manager = get_spotify_auth_manager()
    try:
        token_info = auth_manager.cache_handler.get_cached_token()
    except ValueError:
        return {"status": "error"}

    if token_info is None:
        return {"status": "missing_cache"}

    try:
        auth_manager.validate_token(token_info)
    except SpotifyOauthError as e:
        if e.error == "invalid_grant":
            return {"status": "reauth_required"}
        return {"status": "error"}

    return {"status": "ok"}
