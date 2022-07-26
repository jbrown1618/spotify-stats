import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from utils.path import clear_data, data_path
from utils.settings import spotify_client_id, spotify_client_secret

page_size = 50
small_page_size = 20

queued_artists = set()
queued_albums = set()

processed_playlists = set()
processed_tracks = set()
processed_albums = set()
processed_artists = set()

playlists_data = []
tracks_data = []
artists_data = []
albums_data = []
audio_features = []

liked_tracks = []
playlist_track = []
track_artist = []
album_artist = []
album_track = []
artist_genre = []

def save_data():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_client_id(), 
                                                   client_secret=spotify_client_secret(), 
                                                   redirect_uri="http://localhost:3000/",
                                                   open_browser=False,
                                                   scope="user-library-read"))
    save_playlists_data(sp)
    save_liked_tracks_data(sp)
    save_albums_data(sp)
    save_artists_data(sp)
    save_audio_features_data(sp)

    print('Saving data...')
    clear_data()
    pd.DataFrame(playlists_data).sort_values(by="uri").to_csv(data_path("playlists"), index=False)
    pd.DataFrame(tracks_data).sort_values(by="uri").to_csv(data_path("tracks"), index=False)
    pd.DataFrame(artists_data).sort_values(by="uri").to_csv(data_path("artists"), index=False)
    pd.DataFrame(albums_data).sort_values(by="uri").to_csv(data_path("albums"), index=False)
    pd.DataFrame(liked_tracks).sort_values(by="track_uri").to_csv(data_path("liked_tracks"), index=False)
    pd.DataFrame(playlist_track).sort_values(by=["playlist_uri", "track_uri"]).to_csv(data_path("playlist_track"), index=False)
    pd.DataFrame(track_artist).sort_values(by=["artist_uri", "track_uri"]).to_csv(data_path("track_artist"), index=False)
    pd.DataFrame(album_artist).sort_values(by=["artist_uri", "album_uri"]).to_csv(data_path("album_artist"), index=False)
    pd.DataFrame(album_track).sort_values(by=["album_uri", "track_uri"]).to_csv(data_path("album_track"), index=False)
    pd.DataFrame(audio_features).sort_values(by="track_uri").to_csv(data_path("audio_features"), index=False)
    pd.DataFrame(artist_genre).sort_values(by=["artist_uri", "genre"]).to_csv(data_path("artist_genre"), index=False)


def save_playlists_data(sp: spotipy.Spotify):
    offset = 0
    has_more = True
    while has_more:
        print(f'Fetching {page_size} playlists...')
        playlists = sp.current_user_playlists(limit=page_size, offset=offset)
        for playlist in playlists["items"]:
            process_playlist(playlist)
            save_playlist_tracks_data(sp, playlist["uri"])

        has_more = offset + page_size < playlists["total"]
        offset += page_size


def save_playlist_tracks_data(sp: spotipy.Spotify, playlist_uri):
    offset = 0
    has_more = True
    while has_more:
        print(f'Fetching {page_size} tracks...')
        tracks = sp.playlist_tracks(playlist_uri, limit=page_size, offset=offset)
        for item in tracks["items"]:
            track = item["track"]
            playlist_track.append({ "playlist_uri": playlist_uri, "track_uri": track["uri"] })
            process_track(track)

        has_more = offset + page_size < tracks["total"]
        offset += page_size


def process_playlist(playlist):
    if playlist["uri"] in processed_playlists:
        return

    playlists_data.append(playlist_data(playlist))


def playlist_data(playlist):
    fields = ["name", "collaborative", "public", "uri"]
    data = {field: playlist[field] for field in fields}
    if playlist["images"] is not None and len(playlist["images"]) > 0:
        data["image_url"] = playlist["images"][0]["url"]
    return data


def save_liked_tracks_data(sp: spotipy.Spotify):
    offset = 0
    has_more = True
    while has_more:
        print(f'Fetching {page_size} liked tracks...')
        saved_tracks = sp.current_user_saved_tracks(limit=page_size, offset=offset)

        for item in saved_tracks["items"]:
            track = item["track"]
            liked_tracks.append({ "track_uri": track["uri"] })
            process_track(track)

        has_more = offset + page_size < saved_tracks["total"]
        offset += page_size


def process_track(track):
    if track["uri"] in processed_tracks:
        return

    tracks_data.append(track_data(track))
    processed_tracks.add(track["uri"])
    
    for i, artist in enumerate(track["artists"]):
        track_artist.append({ "track_uri": track["uri"], "artist_uri": artist["uri"], "artist_index": i })
        queue_artist(artist)
    
    album = track["album"]
    album_track.append({ "album_uri": album["uri"], "track_uri": track["uri"] })
    queue_album(album)


def track_data(track):
    fields = ["name", "popularity", "explicit", "duration_ms", "uri"]
    data = {field: track[field] for field in fields}
    data["album_uri"] = track["album"]["uri"]

    return data


def save_albums_data(sp: spotipy.Spotify):
    queue = [album_uri for album_uri in queued_albums]
    while len(queue) > 0:
        next = queue[0:small_page_size]
        queue = queue[small_page_size:]

        print(f'Fetching {len(next)} album details...')
        albums = sp.albums(albums=next)
        for album in albums["albums"]:
            process_album(album)


def queue_album(album):
    if album["uri"] in queued_albums:
        return

    queued_albums.add(album["uri"])


def process_album(album):
    if album["uri"] in processed_albums:
        return

    albums_data.append(album_data(album))
    processed_albums.add(album["uri"])

    for artist in album["artists"]:
        album_artist.append({ "album_uri": album["uri"], "artist_uri": artist["uri"] })
        queue_artist(artist)


def album_data(album):
    fields = ["name", "album_type", "label", "popularity", "total_tracks", "release_date", "uri"]
    data = {field: album[field] for field in fields}

    if album["images"] is not None and len(album["images"]) > 0:
        data["image_url"] = album["images"][0]["url"]

    return data


def save_artists_data(sp: spotipy.Spotify):
    queue = [artist_uri for artist_uri in queued_artists]
    while len(queue) > 0:
        next = queue[0:page_size]
        queue = queue[page_size:]

        print(f'Fetching {len(next)} artist details...')
        artists = sp.artists(artists=next)
        for artist in artists["artists"]:
            process_artist(artist)

            
def queue_artist(artist):
    if artist["uri"] in queued_artists:
        return

    queued_artists.add(artist["uri"])


def process_artist(artist):
    if artist["uri"] in processed_artists:
        return

    for genre in artist["genres"]:
        artist_genre.append({"artist_uri": artist["uri"], "genre": genre})

    artists_data.append(artist_data(artist))
    processed_artists.add(artist["uri"])


def artist_data(artist):
    fields = ["name", "uri", "popularity"]
    data = {field: artist[field] for field in fields}

    data["followers"] = artist["followers"]["total"]

    if artist["images"] is not None and len(artist["images"]) > 0:
        data["image_url"] = artist["images"][0]["url"]

    return data


def save_audio_features_data(sp: spotipy.Spotify):
    queue = [track_uri for track_uri in processed_tracks]
    while len(queue) > 0:
        next = queue[0:page_size]
        queue = queue[page_size:]

        print(f'Fetching {len(next)} audio features...')
        features = sp.audio_features(tracks=next)
        for track_features in features:
            process_audio_features(track_features)


def process_audio_features(features):
    audio_features.append(audio_features_data(features))


def audio_features_data(features):
    fields = ["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"]
    data = {field: features[field] for field in fields}
    data["track_uri"] = features["uri"]
    return data
