import sys
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOauthError, SpotifyStateError

from spotify.spotify_client import get_spotify_auth_manager, spotify_cache_path


def token_needs_reauthorization(error: SpotifyOauthError) -> bool:
    return error.error == "invalid_grant"


def read_authorization_code(auth_manager) -> str:
    print(f"Go to the following URL: {auth_manager.get_authorize_url()}", file=sys.stderr)
    print(
        "After approving access, copy the full loopback URL from your browser's "
        "address bar. It should include a ?code=... query parameter.",
        file=sys.stderr,
    )
    print("Enter the URL you were redirected to: ", end="", file=sys.stderr, flush=True)

    response_url = sys.stdin.readline().strip()
    if not response_url:
        raise SystemExit("No redirected URL entered; authorization aborted.")

    state, code = auth_manager.parse_auth_response_url(response_url)
    if auth_manager.state is not None and auth_manager.state != state:
        raise SpotifyStateError(auth_manager.state, state)

    if code is None:
        raise SystemExit(
            "Expected the redirected loopback URL containing ?code=..., but the "
            "entered URL did not include an authorization code. Do not paste the "
            "Spotify authorization URL shown above."
        )

    return code


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
        auth_manager.get_access_token(
            read_authorization_code(auth_manager),
            as_dict=False,
            check_cache=False,
        )
        token_info = auth_manager.validate_token(
            auth_manager.cache_handler.get_cached_token()
        )
        if token_info is None:
            raise RuntimeError("Spotify authorization succeeded but no token was cached.")

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
