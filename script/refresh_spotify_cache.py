import sys
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOauthError

from spotify.spotify_client import get_spotify_auth_manager, spotify_cache_path


def token_needs_reauthorization(error: SpotifyOauthError) -> bool:
    return error.error == "invalid_grant"


def authorize_with_spotify():
    auth_manager = get_spotify_auth_manager()

    try:
        token_info = auth_manager.validate_token(
            auth_manager.cache_handler.get_cached_token()
        )
    except SpotifyOauthError as e:
        if not token_needs_reauthorization(e):
            raise

        print(
            "Spotify refresh token is invalid; discarding local cache and reauthorizing.",
            file=sys.stderr,
        )
        Path(spotify_cache_path).unlink(missing_ok=True)
        auth_manager = get_spotify_auth_manager()
        token_info = None

    if token_info is None:
        token_info = auth_manager.get_access_token(check_cache=False)

    sp = spotipy.Spotify(
        auth=token_info["access_token"],
        requests_timeout=10,
        retries=2,
    )
    user = sp.current_user()
    print(f"Authorized Spotify user: {user['id']}", file=sys.stderr)


def main():
    authorize_with_spotify()

    with open(spotify_cache_path) as f:
        print(f.read())


if __name__ == "__main__":
    main()
