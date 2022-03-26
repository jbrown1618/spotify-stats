import spotipy
from spotipy.oauth2 import SpotifyOAuth

def main():
    with open('/Users/jbrown1618/Desktop/spotify-client-id') as f:
        client_id = f.read()

    with open('/Users/jbrown1618/Desktop/spotify-client-secret') as f:
        client_secret = f.read()

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                                   client_secret=client_secret, 
                                                   redirect_uri="http://localhost:3000/",
                                                   open_browser=False,
                                                   scope="user-library-read"))

    results = sp.current_user_saved_tracks()

if __name__ == '__main__':
    main()