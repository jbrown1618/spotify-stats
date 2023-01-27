import pandas as pd
from summarize.tables.albums_table import albums_table

from summarize.tables.labels_table import labels_table
from summarize.tables.tracks_table import tracks_table
from utils.markdown import md_table, md_image, md_link
from utils.path import artist_path, artists_path, genre_path, playlist_overview_path

def make_artist_summary(artist: pd.Series, \
                        tracks: pd.DataFrame, \
                        track_artist_full: pd.DataFrame, \
                        album_record_label: pd.DataFrame, \
                        playlists: pd.DataFrame, \
                        artist_genre: pd.DataFrame):
    print(f"Generating summary for artist {artist['artist_name']}")
    file_name = artist_path(artist["artist_name"])
    lines = []

    lines += title(artist)
    lines += image(artist)
    lines += playlists_section(playlists)
    lines += albums_section(tracks)
    lines += labels_section(tracks, album_record_label)
    lines += genres_section(tracks, artist_genre)
    lines += tracks_section(tracks, track_artist_full)

    with open(file_name, "w") as f:
        f.write("\n".join(lines))


def title(artist):
    return ["", f"# {artist['artist_name']}", ""]


def image(artist):
    return ["", md_image(artist["artist_name"], artist["artist_image_url"], 100), ""]


def playlists_section(playlists: pd.DataFrame):
    display_playlists = playlists.sort_values(by="playlist_artist_track_count", ascending=False)
    display_playlists["Art"] = display_playlists["playlist_image_url"].apply(lambda href: md_image("", href, 50))
    display_playlists["Playlist"] = display_playlists["playlist_uri"].apply(lambda uri: display_playlist(uri, playlists))
    display_playlists["Number of Tracks"] = display_playlists["playlist_artist_track_count"]
    display_playlists = display_playlists[["Number of Tracks", "Art", "Playlist"]]

    return [
        '## Featured on Playlists',
        md_table(display_playlists)
    ]


def albums_section(artist_tracks: pd.DataFrame):
    table_data = albums_table(artist_tracks)
    return ["## Top Albums", "", md_table(table_data), ""]


def labels_section(artist_tracks: pd.DataFrame, album_record_label: pd.DataFrame):
    table_data = labels_table(artist_tracks, album_record_label, artists_path())
    return ["## Top Record Labels", "", md_table(table_data), ""]


def genres_section(artist_tracks: pd.DataFrame, artist_genre: pd.DataFrame):
    artist_uri = artist_tracks.iloc[0]["artist_uri"]
    genres_for_artist = artist_genre[artist_genre["artist_uri"] == artist_uri]

    section = ["## Genres", ""]
    for i, g in genres_for_artist.iterrows():
        if g["genre_has_page"]:
            section.append(f"- {md_link(g['genre'], genre_path(g['genre'], artists_path()))}")
        else:
            section.append(f"- {g['genre']}")

    section.append("")
    return section


def tracks_section(tracks: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = tracks_table(tracks, track_artist_full, artists_path())
    return ["## Tracks", "", md_table(display_tracks)]


def display_playlist(playlist_uri: str, playlists: pd.DataFrame):
    playlist = playlists[playlists["playlist_uri"] == playlist_uri].iloc[0]
    return md_link(playlist["playlist_name"], playlist_overview_path(playlist["playlist_name"], artists_path()))
