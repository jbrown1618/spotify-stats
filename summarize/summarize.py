import pandas as pd
from summarize.playlist import make_playlist_summary
from summarize.readme import make_readme
from utils.util import prefix_df


def summarize_results(output_dir):
    album_artist = pd.read_csv(f"{output_dir}/data/album_artist.csv")
    albums = pd.read_csv(f"{output_dir}/data/albums.csv")
    artists = pd.read_csv(f"{output_dir}/data/artists.csv")
    audio_features = pd.read_csv(f"{output_dir}/data/audio_features.csv")
    liked_tracks = pd.read_csv(f"{output_dir}/data/liked_tracks.csv")
    playlist_track = pd.read_csv(f"{output_dir}/data/playlist_track.csv")
    playlists = pd.read_csv(f"{output_dir}/data/playlists.csv")
    track_artist = pd.read_csv(f"{output_dir}/data/track_artist.csv")
    tracks = pd.read_csv(f"{output_dir}/data/tracks.csv")

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

    tracks_full = pd.merge(tracks, audio_features, left_on="track_uri", right_on="track_uri")
    tracks_full = pd.merge(tracks_full, albums, left_on="album_uri", right_on="album_uri")

    track_artist_full = pd.merge(track_artist, artists, left_on="artist_uri", right_on="artist_uri")
    track_artist_full = pd.merge(track_artist_full, artist_track_counts, left_on="artist_uri", right_on="artist_uri")

    make_readme(output_dir, playlists, playlist_track)

    playlists_full = pd.merge(playlists, playlist_track, left_on="playlist_uri", right_on="playlist_uri")
    playlists_full = pd.merge(playlists_full, tracks_full, left_on="track_uri", right_on="track_uri")

    for playlist_uri in playlists["playlist_uri"]:
        playlist_full = playlists_full[playlists_full["playlist_uri"] == playlist_uri]
        if len(playlist_full) == 0:
            continue

        make_playlist_summary(output_dir, playlist_full, track_artist_full)