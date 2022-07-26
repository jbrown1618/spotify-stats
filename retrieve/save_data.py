import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

page_size = 50

def save_data():
    if not os.path.isdir("./output"):
        os.mkdir("./output")

    with open('./spotify-client-id') as f:
        client_id = f.read()

    with open('./spotify-client-secret') as f:
        client_secret = f.read()

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, 
                                                   client_secret=client_secret, 
                                                   redirect_uri="http://localhost:3000/",
                                                   open_browser=False,
                                                   scope="user-library-read"))
    save_tracks_data(sp)


def save_tracks_data(sp: spotipy.Spotify):
    artist_uris = set()
    album_uris = set()

    tracks_data = []
    artists_data = []
    albums_data = []
    track_artist = []
    album_artist = []

    offset = 0
    has_more = True
    while has_more:
        saved_tracks = sp.current_user_saved_tracks(limit=page_size, offset=offset)

        for item in saved_tracks["items"]:
            track = item["track"]
            tracks_data.append(track_data(track))

            for artist in track["artists"]:
                track_artist.append({ "track_uri": track["uri"], "artist_uri": artist["uri"] })

                if (not artist["uri"] in artist_uris):
                    artists_data.append(artist_data(artist))
                    artist_uris.add(artist["uri"])

            album = track["album"]
            if (not album["uri"] in album_uris):
                albums_data.append(album_data(album))
                album_uris.add(album["uri"])

                for artist in album["artists"]:
                    album_artist.append({ "album_uri": album["uri"], "artist_uri": artist["uri"] })
                    if (not artist["uri"] in artist_uris):
                        artists_data.append(artist_data(artist))
                        artist_uris.add(artist["uri"])

        has_more = offset + page_size < saved_tracks["total"]
        offset += page_size

    pd.DataFrame(tracks_data).to_csv("./output/tracks.csv")
    pd.DataFrame(artists_data).to_csv("./output/artists.csv")
    pd.DataFrame(albums_data).to_csv("./output/albums.csv")
    pd.DataFrame(track_artist).to_csv("./output/track_artist.csv")
    pd.DataFrame(album_artist).to_csv("./output/album_artist.csv")


def save_playlists_data(sp: spotipy.Spotify):
    playlists = sp.current_user_playlists()


def track_data(track):
    fields = ["name", "popularity", "explicit", "duration_ms", "uri"]
    data = {field: track[field] for field in fields}
    data["album_uri"] = track["album"]["uri"]
    return data


def artist_data(artist):
    fields = ["name", "uri"]
    data = {field: artist[field] for field in fields}
    return data


def album_data(album):
    fields = ["album_type", "name", "release_date", "uri"]
    data = {field: album[field] for field in fields}
    return data




        # playlists = sp.current_user_playlists()
    # print(playlists)

    # audio_features = sp.audio_features(tracks=['spotify:track:0a0FISfY8ty1xC69xCWf2T'])
    # print(audio_features)

    # ranges = ['short_term', 'medium_term', 'long_term']
    # for sp_range in ranges:
    #     print("range:", sp_range)
    #     results = sp.current_user_top_tracks(time_range=sp_range, limit=50)
    #     for i, item in enumerate(results['items']):
    #         print(i, item['name'], '//', item['artists'][0]['name'])
    #     print()