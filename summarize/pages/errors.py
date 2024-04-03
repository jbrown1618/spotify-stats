import pandas as pd
from data.provider import DataProvider
from data.raw import RawData
from utils.markdown import md_table
from utils.path import errors_path
from utils.util import spotify_link

def make_errors():
    print("Generating Errors")

    content = []
    content += title()
    content += duplicate_tracks()
    content += duplicate_albums()
    content += low_popularity()

    with open(errors_path(), "w") as f:
        f.write("\n".join(content))


def title():
    return [f"# Possible organizational errors", ""]


def duplicate_tracks():
    tracks_with_artists = DataProvider().tracks(owned=True).copy()
    tracks_with_artists["artist_names"] = tracks_with_artists["track_uri"].apply(artist_names_for_track)
    duplicated = tracks_with_artists[tracks_with_artists.duplicated(subset=["track_name", "artist_names"], keep=False)]

    if len(duplicated) == 0:
        return ["## Duplicate tracks", "", "None", ""]

    display = duplicated.copy().sort_values(by=["artist_names", "track_name"])
    display["Track"] = display["track_name"] + " " + display["track_uri"].apply(spotify_link)
    display["Track Popularity"] = display["track_popularity"]
    display["Artists"] = duplicated["track_uri"].apply(display_artists_for_track)
    display["Album"] = display["album_name"] + " " + display["album_uri"].apply(spotify_link)
    display["Album Popularity"] = display["album_popularity"]
    display["Release Date"] = display["album_release_date"]
    display["Label"] = display["album_label"]
    display["Playlists"] = display["track_uri"].apply(display_playlists_for_track)
    display["💚"] = display["track_liked"].apply(lambda liked: "💚" if liked else "")
    display = display[["Track", "Track Popularity", "Release Date", "Artists", "Album", "Album Popularity", "Playlists", "Label", "💚"]]
    table = md_table(display)

    return ["## Duplicate tracks", "", table, ""]


def duplicate_albums():
    albums_with_artists = DataProvider().albums(owned=True).copy()
    albums_with_artists["artist_names_sort"] = albums_with_artists["album_uri"].apply(artist_names_for_album)

    duplicated = albums_with_artists[albums_with_artists.duplicated(subset=["album_name", "artist_names_sort"], keep=False)]

    if len(duplicated) == 0:
        return ['## Duplicate albums', "", "None", ""]

    display = duplicated.copy().sort_values(by=["artist_names_sort", "album_name"])

    display["Album"] = display["album_name"] + " " + display["album_uri"].apply(spotify_link)
    display["Artists"] = duplicated["album_uri"].apply(display_artists_for_album)
    display["Album Popularity"] = display["album_popularity"]
    display["Release Date"] = display["album_release_date"]
    display["Label"] = display["album_label"]
    display["Tracks"] = display["album_uri"].apply(display_tracks_for_album)
    display["Playlists"] = display["album_uri"].apply(display_playlists_for_album)

    display = display[["Album", "Artists", "Album Popularity", "Release Date", "Label", "Tracks", "Playlists"]]

    table = md_table(display)

    return ["## Duplicate albums", "", table, ""]


genres_to_ignore = {'classical', 'a cappella', 'college a cappella', 'classical performance', 'fantasy', 'orchestra', 'classical piano', 'soundtrack'}

def low_popularity():
    tracks_full = DataProvider().tracks(owned=True)
    track_artist = RawData()['track_artist']
    artist_genre = RawData()['artist_genre']
    artists = DataProvider().artists()

    artists_in_ignored_genres = artist_genre[artist_genre['genre'].isin(genres_to_ignore)]['artist_uri']
    artists = artists[~artists['artist_uri'].isin(artists_in_ignored_genres)]
    # Ignore artists with no genres
    artists = artists[artists['artist_uri'].isin(artist_genre['artist_uri'])]

    low_pop_tracks = tracks_full[(tracks_full["track_popularity"] < 3) & (tracks_full["album_popularity"] < 3)]
    high_pop_artists = artists[artists["artist_popularity"] >= 25]

    display = pd.merge(low_pop_tracks, track_artist,  on="track_uri")
    display = pd.merge(display, high_pop_artists, on='artist_uri')

    display = display[["track_name", "album_name", "artist_name", "track_popularity", "album_popularity", "artist_popularity"]]

    return ['## Tracks with low popularity', '', md_table(display), ""]
    

def artist_names_for_album(album_uri: str):
    artists = DataProvider().artists(album_uri=album_uri)
    names = []
    for i, artist in artists.iterrows():
        names.append(artist["artist_name"] + " " + spotify_link(artist["artist_uri"]))

    names.sort()
    return ",<br>".join(names)


def artist_names_for_track(track_uri: str):
    artists = DataProvider().artists(track_uri=track_uri)
    names = [artist["artist_name"].lower() for i, artist in artists.iterrows()]
    names.sort()
    return ",<br>".join(names)


def display_artists_for_track(track_uri: str):
    artists = DataProvider().artists(track_uri=track_uri)
    names = [artist["artist_name"] + " " + spotify_link(artist["artist_uri"]) for i, artist in artists.iterrows()]
    names.sort()
    return ",<br>".join(names)


def display_artists_for_album(album_uri: str):
    artists = DataProvider().artists(album_uri=album_uri)
    names = [
        artist["artist_name"] + " " + spotify_link(artist["artist_uri"]) 
        for i, artist in artists.iterrows() 
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
