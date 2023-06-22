import pandas as pd
from data.provider import DataProvider
from summarize.figures.artist_rank_time_series import artist_rank_time_series
from summarize.pages.track_features import make_track_features_page
from summarize.pages.clusters import make_clusters_page
from summarize.tables.albums_table import albums_table

from summarize.tables.labels_table import labels_table
from summarize.tables.tracks_table import tracks_table
from utils.markdown import md_table, md_image, md_link, md_truncated_table
from utils.path import artist_audio_features_chart_path, artist_audio_features_path, artist_clusters_figure_path, artist_clusters_path, artist_overview_path, artist_path, artist_rank_time_series_path, genre_path, playlist_overview_path
from utils.top_lists import get_term_length_phrase, top_list_terms

def make_artist_summary(artist: pd.Series, \
                        tracks: pd.DataFrame, \
                        playlists: pd.DataFrame, \
                        artist_genre: pd.DataFrame):
    print(f"Generating summary for artist {artist['artist_name']}")
    artist_name = artist["artist_name"]
    content = []

    content += title(artist)
    content += image(artist)
    if len(tracks) > 10:
        content += [md_link(f"See Track Features", artist_audio_features_path(artist_name, artist_path(artist_name))), ""]
        content += [md_link(f"See Clusters", artist_clusters_path(artist_name, artist_path(artist_name))), ""]
    content += top_artists_rank_section(artist)
    content += top_tracks_section(artist)
    content += playlists_section(artist, playlists)
    content += albums_section(tracks)
    content += labels_section(artist_name, tracks)
    content += genres_section(artist, artist_genre)
    content += tracks_section(artist_name, tracks)

    with open(artist_overview_path(artist_name), "w") as f:
        f.write("\n".join(content))

    if len(tracks) > 10:
        make_track_features_page(tracks, artist_name, artist_audio_features_path(artist_name), artist_audio_features_chart_path(artist_name))
        make_clusters_page(tracks, artist_name, artist_clusters_path(artist_name), artist_clusters_figure_path(artist_name))


def title(artist):
    return ["", f"# {artist['artist_name']}", ""]


def image(artist):
    return ["", md_image(artist["artist_name"], artist["artist_image_url"], 100), ""]


def top_artists_rank_section(artist: pd.Series):
    contents = []

    current_entries = DataProvider().top_artists(current=True, artist_uris=[artist['artist_uri']])

    if len(current_entries) > 0:
        rankings_list = [f'{artist["artist_name"]} is currently:']
        for term in top_list_terms:
            entries_for_term = current_entries[current_entries['term'] == term]
            if len(entries_for_term) == 0:
                continue

            rank_for_term = entries_for_term['index'].iloc[0]
            if rank_for_term is None:
                continue
            
            rankings_list.append(f'- The #{rank_for_term} artist of {get_term_length_phrase(term)}')

        contents += rankings_list
        
    time_series = artist_rank_time_series(
        artist['artist_uri'],
        artist['artist_name'],
        artist_rank_time_series_path(artist['artist_name']),
        artist_rank_time_series_path(artist['artist_name'], artist_path(artist['artist_name']))
    )

    if time_series is not None:
        contents += ["", time_series]

    return contents


def top_tracks_section(artist: pd.Series):
    return []


def playlists_section(artist: pd.Series, playlists: pd.DataFrame):
    display_playlists = playlists.copy()
    display_playlists['playlist_artist_track_count'] = display_playlists['playlist_uri']\
        .apply(lambda playlist_uri: track_count_for_artist_in_playlist(playlist_uri, artist['artist_uri']))
    display_playlists = display_playlists.sort_values(by="playlist_artist_track_count", ascending=False)
    display_playlists["Art"] = display_playlists["playlist_image_url"]\
        .apply(lambda href: md_image("", href, 50))
    display_playlists["Playlist"] = display_playlists["playlist_uri"]\
        .apply(lambda uri: display_playlist(artist["artist_name"], uri, playlists))
    display_playlists["Tracks"] = display_playlists["playlist_artist_track_count"]
    display_playlists = display_playlists[["Art", "Tracks", "Playlist"]]

    return [
        '## Featured on Playlists',
        md_table(display_playlists)
    ]


def track_count_for_artist_in_playlist(playlist_uri: str, artist_uri: str) -> int:
    dp = DataProvider()
    tracks_for_artist_in_playlist = dp.tracks(playlist_uri=playlist_uri, artist_uri=artist_uri)
    return len(tracks_for_artist_in_playlist)


def albums_section(artist_tracks: pd.DataFrame):
    table_data = albums_table(artist_tracks)
    return ["## Top Albums", "", md_truncated_table(table_data, 10, "See all albums"), ""]


def labels_section(artist_name: str, artist_tracks: pd.DataFrame):
    table_data = labels_table(artist_tracks, artist_path(artist_name))    
    return ["## Top Record Labels", "", md_table(table_data), ""]


def genres_section(artist: pd.Series, artist_genre: pd.DataFrame):
    artist_uri = artist["artist_uri"]
    artist_name = artist['artist_name']
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


def tracks_section(artist_name: str, tracks: pd.DataFrame):
    display_tracks = tracks_table(tracks, artist_path(artist_name))
    return ["## Tracks", "", md_truncated_table(display_tracks, 10, "See all tracks")]


def display_playlist(artist_name: str, playlist_uri: str, playlists: pd.DataFrame):
    playlist = playlists[playlists["playlist_uri"] == playlist_uri].iloc[0]
    return md_link(playlist["playlist_name"], playlist_overview_path(playlist["playlist_name"], artist_path(artist_name)))
