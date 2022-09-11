import pandas as pd
from utils.path import errors_path
from utils.util import spotify_link

def make_errors(tracks_full: pd.DataFrame, playlists_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    print("Generating Errors")

    content = []
    content += title()
    content += duplicate_tracks(tracks_full, playlists_full, track_artist_full)

    with open(errors_path(), "w") as f:
        f.write("\n".join(content))


def title():
    return [f"# Possible organizational errors", ""]


def duplicate_tracks(tracks_full: pd.DataFrame, playlists_full: pd.DataFrame, track_artist_full: pd.DataFrame):
    tracks_with_artists = tracks_full.copy()
    tracks_with_artists["artist_names"] = tracks_with_artists["track_uri"].apply(lambda uri: artist_names(uri, track_artist_full))
    duplicated = tracks_with_artists[tracks_with_artists.duplicated(subset=["track_name", "artist_names"], keep=False)]

    if len(duplicated) == 0:
        return ["## Duplicate tracks", "", "None", ""]

    display = duplicated.copy().sort_values(by=["artist_names", "track_name"])
    display["Track"] = display["track_name"] + " " + display["track_uri"].apply(lambda uri: spotify_link(uri))
    display["Track Popularity"] = display["track_popularity"]
    display["Artists"] = duplicated["track_uri"].apply(lambda uri: display_artists(uri, track_artist_full))
    display["Album"] = display["album_name"] + " " + display["album_uri"].apply(lambda uri: spotify_link(uri))
    display["Album Popularity"] = display["album_popularity"]
    display["Release Date"] = display["album_release_date"]
    display["Label"] = display["album_label"]
    display["Playlists"] = display["track_uri"].apply(lambda uri: display_playlists(uri, playlists_full))
    display["💚"] = display["track_liked"].apply(lambda liked: "💚" if liked else "")
    display = display[["Track", "Track Popularity", "Release Date", "Artists", "Album", "Album Popularity", "Playlists", "Label", "💚"]]
    table = display.to_markdown(index=False)

    return ["## Duplicate tracks", "", table, ""]


def artist_names(track_uri: str, track_artist_full: pd.DataFrame):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri]
    names = [artist["artist_name"].lower() for i, artist in artists.iterrows()]
    names.sort()
    return ", ".join(names)


def display_artists(track_uri: str, track_artist_full: pd.DataFrame):
    artists = track_artist_full[track_artist_full["track_uri"] == track_uri]
    names = [artist["artist_name"] + " " + spotify_link(artist["artist_uri"]) for i, artist in artists.iterrows()]
    names.sort()
    return ", ".join(names)


def display_playlists(track_uri: str, playlists_full: pd.DataFrame):
    playlists = playlists_full[playlists_full["track_uri"] == track_uri]
    names = [artist["playlist_name"] + " " + spotify_link(artist["playlist_uri"]) for i, artist in playlists.iterrows()]
    names.sort()
    return ", ".join(names)