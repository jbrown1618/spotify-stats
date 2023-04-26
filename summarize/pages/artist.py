import pandas as pd
from summarize.pages.audio_features import make_audio_features_page
from summarize.tables.albums_table import albums_table

from summarize.tables.labels_table import labels_table
from summarize.tables.tracks_table import tracks_table
from utils.markdown import md_table, md_image, md_link, md_truncated_table
from utils.path import artist_audio_features_chart_path, artist_audio_features_path, artist_overview_path, artist_path, genre_path, playlist_overview_path

def make_artist_summary(artist: pd.Series, \
                        tracks: pd.DataFrame, \
                        track_artist_full: pd.DataFrame, \
                        album_record_label: pd.DataFrame, \
                        playlists: pd.DataFrame, \
                        artist_genre: pd.DataFrame):
    print(f"Generating summary for artist {artist['artist_name']}")
    artist_name = artist["artist_name"]
    content = []

    content += title(artist)
    content += image(artist)
    content += [md_link(f"See Audio Features", artist_audio_features_path(artist_name, artist_path(artist_name))), ""]
    content += playlists_section(artist_name, playlists)
    content += albums_section(tracks)
    content += labels_section(artist_name, tracks, album_record_label)
    content += genres_section(artist_name, tracks, artist_genre)
    content += tracks_section(artist_name, tracks, track_artist_full)

    with open(artist_overview_path(artist_name), "w") as f:
        f.write("\n".join(content))

    make_audio_features_page(tracks, artist_name, artist_audio_features_path(artist_name), artist_audio_features_chart_path(artist_name))


def title(artist):
    return ["", f"# {artist['artist_name']}", ""]


def image(artist):
    return ["", md_image(artist["artist_name"], artist["artist_image_url"], 100), ""]


def playlists_section(artist_name: str, playlists: pd.DataFrame):
    display_playlists = playlists.sort_values(by="playlist_artist_track_count", ascending=False)
    display_playlists["Art"] = display_playlists["playlist_image_url"].apply(lambda href: md_image("", href, 50))
    display_playlists["Playlist"] = display_playlists["playlist_uri"].apply(lambda uri: display_playlist(artist_name, uri, playlists))
    display_playlists["Tracks"] = display_playlists["playlist_artist_track_count"]
    display_playlists = display_playlists[["Art", "Tracks", "Playlist"]]

    return [
        '## Featured on Playlists',
        md_table(display_playlists)
    ]


def albums_section(artist_tracks: pd.DataFrame):
    table_data = albums_table(artist_tracks)
    return ["## Top Albums", "", md_truncated_table(table_data, 10, "See all albums"), ""]


def labels_section(artist_name: str, artist_tracks: pd.DataFrame, album_record_label: pd.DataFrame):
    table_data = labels_table(artist_tracks, album_record_label, artist_path(artist_name))
    return ["## Top Record Labels", "", md_table(table_data), ""]


def genres_section(artist_name: str, artist_tracks: pd.DataFrame, artist_genre: pd.DataFrame):
    artist_uri = artist_tracks.iloc[0]["artist_uri"]
    genres_for_artist = artist_genre[artist_genre["artist_uri"] == artist_uri]

    if len(genres_for_artist) == 0:
        return []

    section = ["## Genres", ""]
    for i, g in genres_for_artist.iterrows():
        if g["genre_has_page"]:
            section.append(f"- {md_link(g['genre'], genre_path(g['genre'], artist_path(artist_name)))}")
        else:
            section.append(f"- {g['genre']}")

    section.append("")
    return section


def tracks_section(artist_name: str, tracks: pd.DataFrame, track_artist_full: pd.DataFrame):
    display_tracks = tracks_table(tracks, track_artist_full, artist_path(artist_name))
    return ["## Tracks", "", md_truncated_table(display_tracks, 10, "See all tracks")]


def display_playlist(artist_name: str, playlist_uri: str, playlists: pd.DataFrame):
    playlist = playlists[playlists["playlist_uri"] == playlist_uri].iloc[0]
    return md_link(playlist["playlist_name"], playlist_overview_path(playlist["playlist_name"], artist_path(artist_name)))
