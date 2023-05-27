import pandas as pd
from data.provider import DataProvider
from utils.markdown import md_table
from utils.path import errors_path
from utils.util import spotify_link

def make_errors(tracks_full: pd.DataFrame, track_artist_full: pd.DataFrame, albums: pd.DataFrame, album_artist: pd.DataFrame, artists: pd.DataFrame):
    print("Generating Errors")

    content = []
    content += title()
    content += duplicate_tracks(tracks_full, track_artist_full)
    content += duplicate_albums(albums, album_artist, artists)
    content += low_popularity(tracks_full, track_artist_full)

    with open(errors_path(), "w") as f:
        f.write("\n".join(content))


def title():
    return [f"# Possible organizational errors", ""]


def duplicate_tracks(tracks_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    tracks_with_artists = tracks_full.copy()
    tracks_with_artists["artist_names"] = tracks_with_artists["track_uri"].apply(lambda uri: artist_names_for_track(uri, track_artist_full))
    duplicated = tracks_with_artists[tracks_with_artists.duplicated(subset=["track_name", "artist_names"], keep=False)]

    if len(duplicated) == 0:
        return ["## Duplicate tracks", "", "None", ""]

    display = duplicated.copy().sort_values(by=["artist_names", "track_name"])
    display["Track"] = display["track_name"] + " " + display["track_uri"].apply(lambda uri: spotify_link(uri))
    display["Track Popularity"] = display["track_popularity"]
    display["Artists"] = duplicated["track_uri"].apply(lambda track_uri: display_artists_for_track(track_uri, track_artist_full))
    display["Album"] = display["album_name"] + " " + display["album_uri"].apply(lambda uri: spotify_link(uri))
    display["Album Popularity"] = display["album_popularity"]
    display["Release Date"] = display["album_release_date"]
    display["Label"] = display["album_label"]
    display["Playlists"] = display["track_uri"].apply(display_playlists_for_track)
    display["💚"] = display["track_liked"].apply(lambda liked: "💚" if liked else "")
    display = display[["Track", "Track Popularity", "Release Date", "Artists", "Album", "Album Popularity", "Playlists", "Label", "💚"]]
    table = md_table(display)

    return ["## Duplicate tracks", "", table, ""]


def duplicate_albums(albums: pd.DataFrame, album_artist: pd.DataFrame, artists: pd.DataFrame):
    albums_with_artists = albums.copy()
    albums_with_artists["artist_names_sort"] = albums_with_artists["album_uri"].apply(lambda uri: artist_names_for_album(uri, album_artist, artists))

    duplicated = albums_with_artists[albums_with_artists.duplicated(subset=["album_name", "artist_names_sort"], keep=False)]

    if len(duplicated) == 0:
        return ['## Duplicate albums', "", "None", ""]

    display = duplicated.copy().sort_values(by=["artist_names_sort", "album_name"])

    display["Album"] = display["album_name"] + " " + display["album_uri"].apply(lambda uri: spotify_link(uri))
    display["Artists"] = duplicated["album_uri"].apply(lambda uri: display_artists_for_album(uri, album_artist, artists))
    display["Album Popularity"] = display["album_popularity"]
    display["Release Date"] = display["album_release_date"]
    display["Label"] = display["album_label"]
    display["Tracks"] = display["album_uri"].apply(display_tracks_for_album)
    display["Playlists"] = display["album_uri"].apply(display_playlists_for_album)

    display = display[["Album", "Artists", "Album Popularity", "Release Date", "Label", "Tracks", "Playlists"]]

    table = md_table(display)

    return ["## Duplicate albums", "", table, ""]


def low_popularity(tracks_full, track_artist_full):
    low_pop_tracks = tracks_full[(tracks_full["track_popularity"] < 3) & (tracks_full["album_popularity"] < 3)]
    high_pop_artists = track_artist_full[track_artist_full["artist_popularity"] >= 25]

    display = pd.merge(low_pop_tracks, high_pop_artists,  on="track_uri")

    display = display[["track_name", "album_name", "artist_name", "track_popularity", "album_popularity", "artist_popularity"]]

    return ['## Tracks with low popularity', '', md_table(display), ""]
    


def artist_names_for_album(album_uri: str, album_artist: pd.DataFrame, artists: pd.DataFrame):
    artist_uris = set(album_artist[album_artist["album_uri"] == album_uri]["artist_uri"])
    names = []
    for artist_uri in artist_uris:
        artist = artists[artists["artist_uri"] == artist_uri].iloc[0]
        names.append(artist["artist_name"] + " " + spotify_link(artist["artist_uri"]))

    names.sort()
    return ",<br>".join(names)


def artist_names_for_track(track_uri: str, track_artist_full: pd.DataFrame):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri]
    names = [artist["artist_name"].lower() for i, artist in artists.iterrows()]
    names.sort()
    return ",<br>".join(names)


def display_artists_for_track(track_uri: str, track_artist_full: pd.DataFrame):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri]
    names = [artist["artist_name"] + " " + spotify_link(artist["artist_uri"]) for i, artist in artists.iterrows()]
    names.sort()
    return ",<br>".join(names)


def display_artists_for_album(album_uri: str, album_artist: pd.DataFrame, artists: pd.DataFrame):
    artist_uris = set(album_artist[album_artist["album_uri"] == album_uri]["artist_uri"])
    names = [
        artist["artist_name"] + " " + spotify_link(artist["artist_uri"]) 
        for i, artist in artists.iterrows() 
        if artist["artist_uri"] in artist_uris
    ]
    names.sort()
    return ",<br>".join(names)


def display_playlists_for_track(track_uri: str):
    playlists = DataProvider().playlists(track_uri=track_uri)
    names = [
        playlist["playlist_name"] + " " + spotify_link(playlist["playlist_uri"]) 
        for i, playlist 
        in playlists.iterrows()
    ]
    names.sort()
    return ",<br>".join(names)


def display_playlists_for_album(album_uri: str):
    playlists = DataProvider().playlists(album_uri=album_uri)
    names = [
        playlist["playlist_name"] + " " + spotify_link(playlist["playlist_uri"]) 
        for i, playlist 
        in playlists.iterrows()
    ]
    names.sort()
    return ",<br>".join(names)


def display_tracks_for_album(album_uri: str):
    all_tracks = DataProvider().tracks()
    tracks = all_tracks[all_tracks["album_uri"] == album_uri]
    names = [
        track["track_name"] + " " + spotify_link(track["track_uri"]) 
        for i, track 
        in tracks.iterrows()
    ]
    names.sort()
    return ",<br>".join(names)
