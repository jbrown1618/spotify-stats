import pandas as pd
from summarize.artist import make_artist_summary
from summarize.playlist import make_playlist_summary
from summarize.readme import make_readme
from utils.settings import output_dir
from utils.util import prefix_df


def summarize_results():
    album_artist = pd.read_csv(f"{output_dir()}/data/album_artist.csv")
    albums = pd.read_csv(f"{output_dir()}/data/albums.csv")
    artists = pd.read_csv(f"{output_dir()}/data/artists.csv")
    audio_features = pd.read_csv(f"{output_dir()}/data/audio_features.csv")
    liked_tracks = pd.read_csv(f"{output_dir()}/data/liked_tracks.csv")
    playlist_track = pd.read_csv(f"{output_dir()}/data/playlist_track.csv")
    playlists = pd.read_csv(f"{output_dir()}/data/playlists.csv")
    track_artist = pd.read_csv(f"{output_dir()}/data/track_artist.csv")
    tracks = pd.read_csv(f"{output_dir()}/data/tracks.csv")

    prefixes = ["album_", "track_", "playlist_", "artist_"]
    prefix_df(albums, "album_", prefixes)
    prefix_df(tracks, "track_", prefixes)
    prefix_df(audio_features, "audio_", prefixes)
    prefix_df(playlists, "playlist_", prefixes)
    prefix_df(artists, "artist_", prefixes)

    artist_track_counts = track_artist.groupby("artist_uri").count().reset_index()
    artist_track_counts.rename(columns={"track_uri": "artist_track_count"}, inplace=True)
    artist_track_counts["artist_has_page"] = artist_track_counts["artist_track_count"] >= 10
    artists_with_page = {artist_uri for artist_uri in artist_track_counts[artist_track_counts["artist_has_page"]]["artist_uri"] }

    artist_playlist = pd.merge(track_artist, playlist_track, on="track_uri").groupby(["artist_uri", "playlist_uri"]).count().reset_index()
    artist_playlist.rename(columns={"track_uri": "playlist_artist_track_count"}, inplace=True)

    tracks_full = pd.merge(tracks, audio_features, on="track_uri")
    tracks_full = pd.merge(tracks_full, albums, on="album_uri")
    liked_track_uris = { uri for uri in liked_tracks["track_uri"] }
    tracks_full["track_liked"] = tracks_full["track_uri"].apply(lambda uri: uri in liked_track_uris)

    artists_full = pd.merge(artists, artist_track_counts, on="artist_uri")

    track_artist_full = pd.merge(track_artist, artists_full, on="artist_uri")

    make_readme(playlists, playlist_track)

    playlists_full = pd.merge(playlists, playlist_track, on="playlist_uri")
    playlists_full = pd.merge(playlists_full, tracks_full, on="track_uri")

    for playlist_uri in playlists["playlist_uri"]:
        playlist_full = playlists_full[playlists_full["playlist_uri"] == playlist_uri]
        if len(playlist_full) == 0:
            continue

        make_playlist_summary(playlist_full, track_artist_full)

    for artist_uri in artists_with_page:
        artist = artists_full[artists_full["artist_uri"] == artist_uri].iloc[0]        
        tracks_for_artist = track_artist[track_artist["artist_uri"] == artist_uri]
        tracks_for_artist = pd.merge(tracks_for_artist, tracks_full, on="track_uri")
        make_artist_summary(artist, tracks_for_artist)