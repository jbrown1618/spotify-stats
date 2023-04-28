import pandas as pd

from data.provider import DataProvider
from data.raw import RawData
from summarize.pages.artist import make_artist_summary
from summarize.pages.genre import make_genre_summary
from summarize.pages.label import make_label_summary
from summarize.pages.playlist import make_playlist_summary
from summarize.pages.overview import make_overview
from summarize.pages.errors import make_errors
from utils.path import clear_markdown


def summarize_results():
    raw_data = RawData()
    album_artist = raw_data['album_artist']
    artists = raw_data["artists"]
    liked_tracks = raw_data["liked_tracks"]
    playlist_track = raw_data["playlist_track"]
    playlists = raw_data["playlists"]
    track_artist = raw_data["track_artist"]
    artist_genre = raw_data["artist_genre"]
    top_tracks = raw_data["top_tracks"]
    top_artists = raw_data["top_artists"]

    dp = DataProvider()

    artist_liked_tracks = pd.merge(track_artist, liked_tracks, on="track_uri").groupby("artist_uri").agg({"track_uri": "count"}).reset_index()
    artist_liked_tracks.rename(columns={"track_uri": "artist_liked_track_count"}, inplace=True)
    artist_all_track_counts = track_artist[["artist_uri", "track_uri"]].groupby("artist_uri").agg({"track_uri": "count"}).reset_index()
    artist_all_track_counts.rename(columns={"track_uri": "artist_track_count"}, inplace=True)

    artist_track_counts = pd.merge(artist_liked_tracks, artist_all_track_counts, how="outer", on="artist_uri")
    artist_track_counts.fillna(0, inplace=True)
    
    artist_track_counts["artist_has_page"] = (artist_track_counts["artist_track_count"] >= 10) & (artist_track_counts["artist_liked_track_count"] > 0)
    artists_with_page = {artist_uri for artist_uri in artist_track_counts[artist_track_counts["artist_has_page"]]["artist_uri"] }

    artist_playlist = pd.merge(track_artist, playlist_track, on="track_uri").groupby(["artist_uri", "playlist_uri"]).count().reset_index()
    artist_playlist.rename(columns={"track_uri": "playlist_artist_track_count"}, inplace=True)
    artist_playlist_full = pd.merge(artist_playlist, playlists, on="playlist_uri")

    artists_full = pd.merge(artists, artist_track_counts, on="artist_uri")

    track_artist_full = pd.merge(track_artist, artists_full, on="artist_uri")

    playlists_full = pd.merge(playlists, playlist_track, on="playlist_uri")
    playlists_full = pd.merge(playlists_full, dp.tracks(), on="track_uri")

    track_primary_artist = pd.merge(dp.tracks(), track_artist[track_artist["artist_index"] == 0], on="track_uri")
    track_genre = pd.merge(track_primary_artist, artist_genre, on="artist_uri")
    track_genre.drop(columns=["artist_uri"], inplace=True)
    genre_track_counts = track_genre.groupby("genre").agg({"track_uri": "count", "track_liked": "sum"}).reset_index()
    genres_with_page = set(genre_track_counts[(genre_track_counts["track_uri"] >= 40) & (genre_track_counts["track_liked"] > 0)]["genre"])
    artist_genre["genre_has_page"] = artist_genre["genre"].apply(lambda genre: genre in genres_with_page)
    track_genre["genre_has_page"] = track_genre["genre"].apply(lambda genre: genre in genres_with_page)

    clear_markdown()

    make_overview(playlists, playlist_track, dp.tracks(), track_genre, track_artist_full, top_tracks, top_artists)
    make_errors(dp.tracks(), playlists_full, track_artist_full, dp.albums(), album_artist, artists)

    make_playlist_summary(dp.tracks(liked=True), track_artist_full, track_genre, is_liked_songs=True)

    for playlist_uri in playlists["playlist_uri"]:
        playlist_full = playlists_full[playlists_full["playlist_uri"] == playlist_uri]
        if len(playlist_full) == 0:
            continue

        make_playlist_summary(playlist_full, track_artist_full, track_genre)

    for artist_uri in artists_with_page:
        artist = artists_full[artists_full["artist_uri"] == artist_uri].iloc[0]        
        tracks_for_artist = track_artist[track_artist["artist_uri"] == artist_uri]
        tracks_for_artist = pd.merge(tracks_for_artist, dp.tracks(), on="track_uri")

        playlists_for_artist = artist_playlist_full[artist_playlist_full["artist_uri"] == artist_uri]
        make_artist_summary(artist, tracks_for_artist, track_artist_full, playlists_for_artist, artist_genre)

    for standardized_label in dp.labels(with_page=True)['album_standardized_label']:
        make_label_summary(standardized_label, dp.tracks(label=standardized_label), track_artist_full, track_genre)

    for genre in genres_with_page:
        tracks_in_genre = track_genre[track_genre["genre"] == genre]
        make_genre_summary(tracks_in_genre, track_artist_full)
