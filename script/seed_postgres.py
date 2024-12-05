"""
A script for seeding a postgres database from a collection of csv files (the old storage format)

The data mode setting should be "sql"
"""
import pandas as pd

from data.raw import RawData
from utils.path import data_path, persistent_data_path

raw = RawData()

albums = pd.read_csv(data_path("spotify", "albums"))
albums['name'] = albums['name'].fillna('NA') # pandas silliness
raw['albums'] = albums
raw['artists'] = pd.read_csv(data_path("spotify", "artists"))
raw['playlists'] = pd.read_csv(data_path("spotify", "playlists"))
raw['tracks'] = pd.read_csv(data_path("spotify", "tracks"))

raw['liked_tracks'] = pd.read_csv(data_path("spotify", "liked_tracks"))

raw['top_tracks'] = pd.read_csv(persistent_data_path("spotify", "top_tracks", "2023"))
raw['top_tracks'] = pd.read_csv(persistent_data_path("spotify", "top_tracks", "2024"))
raw['top_artists'] = pd.read_csv(persistent_data_path("spotify", "top_artists", "2023"))
raw['top_artists'] = pd.read_csv(persistent_data_path("spotify", "top_artists", "2024"))

raw['album_artist'] = pd.read_csv(data_path("spotify", "album_artist"))
raw['artist_genre'] = pd.read_csv(data_path("spotify", "artist_genre"))
raw['playlist_track'] = pd.read_csv(data_path("spotify", "playlist_track"))
raw['track_artist'] = pd.read_csv(data_path("spotify", "track_artist"))

raw['mb_artist_relationships'] = pd.read_csv(data_path("musicbrainz", "mb_artist_relationships"))
raw['mb_artists'] = pd.read_csv(data_path("musicbrainz", "mb_artists"))
raw['mb_recording_credits'] = pd.read_csv(data_path("musicbrainz", "mb_recording_credits"))
raw['mb_recordings'] = pd.read_csv(data_path("musicbrainz", "mb_recordings"))
raw['mb_unfetchable_isrcs'] = pd.read_csv(data_path("musicbrainz", "mb_unfetchable_isrcs"))
raw['mb_unmatchable_artists'] = pd.read_csv(data_path("musicbrainz", "mb_unmatchable_artists"))
raw['sp_artist_mb_artist'] = pd.read_csv(data_path("musicbrainz", "sp_artist_mb_artist"))
raw['sp_track_mb_recording'] = pd.read_csv(data_path("musicbrainz", "sp_track_mb_recording"))
