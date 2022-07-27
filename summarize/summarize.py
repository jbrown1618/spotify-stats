import pandas as pd
from summarize.readme import make_readme


def summarize_results(output_dir):
    album_artist = pd.read_csv(f"{output_dir}/data/album_artist.csv")
    album_track = pd.read_csv(f"{output_dir}/data/album_track.csv")
    albums = pd.read_csv(f"{output_dir}/data/albums.csv", index_col="uri")
    artists = pd.read_csv(f"{output_dir}/data/artists.csv", index_col="uri")
    audio_features = pd.read_csv(f"{output_dir}/data/audio_features.csv", index_col="track_uri")
    liked_tracks = pd.read_csv(f"{output_dir}/data/liked_tracks.csv", index_col="track_uri")
    playlist_track = pd.read_csv(f"{output_dir}/data/playlist_track.csv")
    playlists = pd.read_csv(f"{output_dir}/data/playlists.csv", index_col="uri")
    track_artist = pd.read_csv(f"{output_dir}/data/track_artist.csv")
    tracks = pd.read_csv(f"{output_dir}/data/tracks.csv", index_col="uri")

    make_readme(output_dir, playlists, playlist_track)