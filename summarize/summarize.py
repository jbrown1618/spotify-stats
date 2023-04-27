import pandas as pd

from data.raw import RawData
from summarize.pages.artist import make_artist_summary
from summarize.pages.genre import make_genre_summary
from summarize.pages.label import make_label_summary
from summarize.pages.playlist import make_playlist_summary
from summarize.pages.overview import make_overview
from summarize.pages.errors import make_errors
from utils.album import short_album_name
from utils.audio_features import set_tracks_full
from utils.date import release_year
from utils.path import clear_markdown
from utils.record_label import standardize_record_labels
from utils.util import first


def summarize_results():
    raw_data = RawData()
    album_artist = raw_data['album_artist']
    albums = raw_data["albums"]
    artists = raw_data["artists"]
    audio_features = raw_data["audio_features"]
    liked_tracks = raw_data["liked_tracks"]
    playlist_track = raw_data["playlist_track"]
    playlists = raw_data["playlists"]
    track_artist = raw_data["track_artist"]
    tracks = raw_data["tracks"]
    artist_genre = raw_data["artist_genre"]
    top_tracks = raw_data["top_tracks"]
    top_artists = raw_data["top_artists"]

    albums['album_release_year'] = albums['album_release_date'].apply(release_year)
    albums['album_short_name'] = albums['album_name'].apply(short_album_name)

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

    tracks_full = pd.merge(tracks, audio_features, on="track_uri")
    tracks_full = pd.merge(tracks_full, albums, on="album_uri")
    liked_track_uris = { uri for uri in liked_tracks["track_uri"] }
    tracks_full["track_liked"] = tracks_full["track_uri"].apply(lambda uri: uri in liked_track_uris)

    liked_tracks_full = pd.merge(liked_tracks, tracks_full, on="track_uri")

    artists_full = pd.merge(artists, artist_track_counts, on="artist_uri")

    track_artist_full = pd.merge(track_artist, artists_full, on="artist_uri")

    playlists_full = pd.merge(playlists, playlist_track, on="playlist_uri")
    playlists_full = pd.merge(playlists_full, tracks_full, on="track_uri")

    track_primary_artist = pd.merge(tracks_full, track_artist[track_artist["artist_index"] == 0], on="track_uri")
    track_genre = pd.merge(track_primary_artist, artist_genre, on="artist_uri")
    track_genre.drop(columns=["artist_uri"], inplace=True)
    genre_track_counts = track_genre.groupby("genre").agg({"track_uri": "count", "track_liked": "sum"}).reset_index()
    genres_with_page = set(genre_track_counts[(genre_track_counts["track_uri"] >= 40) & (genre_track_counts["track_liked"] > 0)]["genre"])
    artist_genre["genre_has_page"] = artist_genre["genre"].apply(lambda genre: genre in genres_with_page)
    track_genre["genre_has_page"] = track_genre["genre"].apply(lambda genre: genre in genres_with_page)


    set_tracks_full(tracks_full)

    album_record_label = standardize_record_labels(albums, tracks)

    clear_markdown()

    make_overview(playlists, playlist_track, tracks_full, track_genre, track_artist_full, album_record_label, top_tracks, top_artists)
    make_errors(tracks_full, playlists_full, track_artist_full, albums, album_artist, artists)

    make_playlist_summary(liked_tracks_full, track_artist_full, album_record_label, track_genre, is_liked_songs=True)

    for playlist_uri in playlists["playlist_uri"]:
        playlist_full = playlists_full[playlists_full["playlist_uri"] == playlist_uri]
        if len(playlist_full) == 0:
            continue

        make_playlist_summary(playlist_full, track_artist_full, album_record_label, track_genre)


    for artist_uri in artists_with_page:
        artist = artists_full[artists_full["artist_uri"] == artist_uri].iloc[0]        
        tracks_for_artist = track_artist[track_artist["artist_uri"] == artist_uri]
        tracks_for_artist = pd.merge(tracks_for_artist, tracks_full, on="track_uri")

        playlists_for_artist = artist_playlist_full[artist_playlist_full["artist_uri"] == artist_uri]
        make_artist_summary(artist, tracks_for_artist, track_artist_full, album_record_label, playlists_for_artist, artist_genre)


    labels_by_page = album_record_label.groupby("album_standardized_label").agg({"label_has_page": first}).reset_index()
    labels_to_summarize = set(labels_by_page[labels_by_page["label_has_page"]]["album_standardized_label"])
    for standardized_label in labels_to_summarize:
        albums_under_label = album_record_label[album_record_label["album_standardized_label"] == standardized_label][["album_uri"]]
        label_full = pd.merge(tracks_full, albums_under_label, on="album_uri")
        make_label_summary(standardized_label, label_full, track_artist_full, track_genre)


    for genre in genres_with_page:
        tracks_in_genre = track_genre[track_genre["genre"] == genre]
        make_genre_summary(tracks_in_genre, track_artist_full, album_record_label)
