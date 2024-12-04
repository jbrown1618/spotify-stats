import pandas as pd
import sqlalchemy

from utils.path import data_path, persistent_data_path
from utils.settings import postgres_host, postgres_password, postgres_user

engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{postgres_user()}:{postgres_password()}@{postgres_host()}/spotifystats")

with engine.begin() as conn:
    albums = pd.read_csv(data_path("spotify", "albums"))
    albums['name'] = albums['name'].fillna('NA') # pandas silliness
    albums.to_sql("album", conn, if_exists="append", index=False)

    pd.read_csv(data_path("spotify", "artists"))\
    .to_sql("artist", conn, if_exists="append", index=False)

    pd.read_csv(data_path("spotify", "playlists"))\
    .to_sql("playlist", conn, if_exists="append", index=False)

    pd.read_csv(data_path("spotify", "tracks"))\
    .to_sql("track", conn, if_exists="append", index=False)



    pd.read_csv(data_path("spotify", "liked_tracks"))\
    .to_sql("liked_track", conn, if_exists="append", index=False)

    top_tracks_2023 = pd.read_csv(persistent_data_path("spotify", "top_tracks", "2023"))
    top_tracks_2023.drop_duplicates(subset=['index', 'term', 'as_of_date'], inplace=True)
    top_tracks_2023.to_sql("top_track", conn, if_exists="append", index=False)

    top_tracks_2024 = pd.read_csv(persistent_data_path("spotify", "top_tracks", "2024"))
    top_tracks_2024.drop_duplicates(subset=['index', 'term', 'as_of_date'], inplace=True)
    top_tracks_2024.to_sql("top_track", conn, if_exists="append", index=False)

    top_artists_2023 = pd.read_csv(persistent_data_path("spotify", "top_artists", "2023"))
    top_artists_2023.drop_duplicates(subset=['index', 'term', 'as_of_date'], inplace=True)
    top_artists_2023.to_sql("top_artist", conn, if_exists="append", index=False)

    top_artists_2024 = pd.read_csv(persistent_data_path("spotify", "top_artists", "2024"))
    top_artists_2024.drop_duplicates(subset=['index', 'term', 'as_of_date'], inplace=True)
    top_artists_2024.to_sql("top_artist", conn, if_exists="append", index=False)



    pd.read_csv(data_path("spotify", "album_artist"))\
    .to_sql("album_artist", conn, if_exists="append", index=False)

    pd.read_csv(data_path("spotify", "artist_genre"))\
    .to_sql("artist_genre", conn, if_exists="append", index=False)

    pt = pd.read_csv(data_path("spotify", "playlist_track"))
    pt.drop_duplicates(subset=['playlist_uri', 'track_uri'], inplace=True)
    pt.to_sql("playlist_track", conn, if_exists="append", index=False)

    pd.read_csv(data_path("spotify", "track_artist"))\
    .to_sql("track_artist", conn, if_exists="append", index=False)



    pd.read_csv(data_path("musicbrainz", "mb_artist_relationships"))\
    .to_sql("mb_artist_relationship", conn, if_exists="append", index=False)

    pd.read_csv(data_path("musicbrainz", "mb_artists"))\
    .to_sql("mb_artist", conn, if_exists="append", index=False)

    pd.read_csv(data_path("musicbrainz", "mb_recording_credits"))\
    .to_sql("mb_recording_credit", conn, if_exists="append", index=False)

    pd.read_csv(data_path("musicbrainz", "mb_recordings"))\
    .to_sql("mb_recording", conn, if_exists="append", index=False)

    pd.read_csv(data_path("musicbrainz", "mb_unfetchable_isrcs"))\
    .to_sql("mb_unfetchable_isrc", conn, if_exists="append", index=False)

    pd.read_csv(data_path("musicbrainz", "mb_unmatchable_artists"))\
    .to_sql("mb_unmatchable_artist", conn, if_exists="append", index=False)

    pd.read_csv(data_path("musicbrainz", "sp_artist_mb_artist"))\
    .to_sql("sp_artist_mb_artist", conn, if_exists="append", index=False)

    pd.read_csv(data_path("musicbrainz", "sp_track_mb_recording"))\
    .to_sql("sp_track_mb_recording", conn, if_exists="append", index=False)
