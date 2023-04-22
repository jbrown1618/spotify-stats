import pandas as pd
from summarize.figures.artists_bar_chart import artists_bar_chart
from summarize.figures.genres_bar_chart import genres_bar_chart
from summarize.figures.labels_bar_chart import labels_bar_chart
from summarize.pages.audio_features import make_audio_features_page
from summarize.tables.artists_table import artists_table
from summarize.tables.genres_table import genres_table
from summarize.tables.labels_table import labels_table
from summarize.tables.playlists_table import playlists_table
from summarize.tables.top_artists_table import top_artists_table
from summarize.tables.top_tracks_table import top_tracks_table
from utils.artist import get_primary_artist_name
from utils.audio_features import comparison_scatter_plot
from utils.markdown import md_link, md_truncated_table
from utils.path import errors_path, overview_artist_graph_path, overview_artists_scatterplot_path, overview_audio_features_path, overview_genre_graph_path, overview_genres_scatterplot_path, overview_label_graph_path, overview_playlists_scatterplot_path, pairplot_path, overview_path
from utils.settings import output_dir
from utils.util import first

def make_overview(playlists: pd.DataFrame, playlist_track: pd.DataFrame, tracks_full: pd.DataFrame, track_genre: pd.DataFrame, track_artist_full: pd.DataFrame, album_record_label: pd.DataFrame, top_tracks: pd.DataFrame, top_artists: pd.DataFrame):
    print("Generating Overview")

    content = []

    content += title("jbrown1618")
    content += byline()
    content += [md_link(f"See Audio Features", overview_audio_features_path()), ""]
    content += top_tracks_and_artists_section(top_tracks, tracks_full, top_artists, track_artist_full)
    content += playlists_section(playlists, playlist_track, tracks_full)
    content += artists_section(tracks_full, track_artist_full)
    content += genres_section(tracks_full, track_genre)
    content += labels_section(tracks_full, album_record_label)
    content += errors()

    with open(overview_path(), "w") as f:
        f.write("\n".join(content))

    make_audio_features_page(tracks_full, "All Tracks", overview_audio_features_path(output_dir()))


def title(user: str):
    return [f"# Spotify Summary for {user}", ""]


def byline():
    return [f"Generated by {md_link('jbrown1618/spotify-stats', 'https://github.com/jbrown1618/spotify-stats')}", ""]


def errors():
    return ['## Possible organizational errors', md_link("Possible organizational errors", errors_path(output_dir()))]


def top_tracks_and_artists_section(top_tracks: pd.DataFrame, tracks: pd.DataFrame, top_artists: pd.DataFrame, track_artist_full: pd.DataFrame):
    artists = track_artist_full.groupby("artist_uri").agg({"artist_name": first, "artist_image_url": first}).reset_index()
    return [
        "## Top Tracks", 
        "", 
        md_truncated_table(top_tracks_table(top_tracks, tracks), 10, "See top 50 tracks"), 
        "",
        "Top Artists",
        "",
        md_truncated_table(top_artists_table(top_artists, artists), 10, "See top 50 artists"), 
        ""
    ]


def playlists_section(playlists: pd.DataFrame, playlist_track: pd.DataFrame, tracks_full: pd.DataFrame):
    playlist_display_data = pd.merge(playlists, playlist_track, on="playlist_uri")
    playlist_display_data = pd.merge(playlist_display_data, tracks_full, on="track_uri")
    track_counts = playlist_display_data\
        .groupby("playlist_uri")\
        .agg({"track_uri": "count", "track_liked": "sum"})\
        .reset_index()

    table = md_truncated_table(playlists_table(playlists, playlist_track, tracks_full, output_dir()), 10)

    playlists_sorted_by_track_count = track_counts.sort_values(by="track_uri", ascending=False)["playlist_uri"]
    main_playlist_col = tracks_full["track_uri"].apply(lambda track_uri: get_main_playlist(track_uri, playlist_track, playlists, playlists_sorted_by_track_count))
    scatter = comparison_scatter_plot(tracks_full, main_playlist_col, "Playlist", overview_playlists_scatterplot_path(), overview_playlists_scatterplot_path(output_dir()))
    
    return [
        "## Playlists", 
        "", 
        table, 
        "", 
        scatter, 
        ""
    ]


def artists_section(tracks: pd.DataFrame, track_artist_full: pd.DataFrame):
    img = artists_bar_chart(tracks, track_artist_full, overview_artist_graph_path(), overview_artist_graph_path(output_dir()))
    table_data = artists_table(tracks, track_artist_full, output_dir())

    summary = f"See all {len(table_data)} artists"
    if len(table_data) > 100:
        summary = "See top 100 artists"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    if len(table_data) >= 10:
        scatterplot = comparison_scatter_plot(
            tracks, 
            tracks["track_uri"].apply(lambda uri: get_primary_artist_name(uri, track_artist_full)), 
            "Artist", 
            overview_artists_scatterplot_path(), 
            overview_artists_scatterplot_path(output_dir())
        )
    else:
        scatterplot = ""

    return ["## Artists", "", full_list, "", img, "", scatterplot , ""]


def genres_section(tracks: pd.DataFrame, track_genre: pd.DataFrame):
    img = genres_bar_chart(tracks, track_genre, overview_genre_graph_path(), overview_genre_graph_path(output_dir()))
    main_genre_col = tracks["track_uri"].apply(lambda track_uri: get_main_genre(track_uri, track_genre))
    scatter = comparison_scatter_plot(tracks, main_genre_col, "Genre", overview_genres_scatterplot_path(), overview_genres_scatterplot_path(output_dir()))

    table_data = genres_table(tracks, track_genre, output_dir())
    
    summary = f"See all {len(table_data)} genres"
    if len(table_data) > 100:
        summary = "See top 100 genres"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Genres", "", full_list, "", img, "", scatter, ""]


def get_main_genre(track_uri: str, track_genre: pd.DataFrame):
    subset = track_genre[track_genre["track_uri"] == track_uri]
    if len(subset) == 0:
        return "None"

    return subset.iloc[0]["genre"]


def get_main_playlist(track_uri: str, playlist_track: pd.DataFrame, playlists: pd.DataFrame, playlists_sorted_by_track_count):
    playlist_uris = set(playlist_track[playlist_track["track_uri"] == track_uri]["playlist_uri"])
    for playlist_uri in playlists_sorted_by_track_count:
        if playlist_uri in playlist_uris:
            return playlists[playlists["playlist_uri"] == playlist_uri].iloc[0]["playlist_name"]
    return "None"


def labels_section(tracks: pd.DataFrame, album_record_label: pd.DataFrame):
    img = labels_bar_chart(tracks, album_record_label, overview_label_graph_path(), overview_label_graph_path(output_dir()))
    table_data = labels_table(tracks, album_record_label, output_dir())

    summary = f"See all {len(table_data)} labels"
    if len(table_data) > 100:
        summary = "See top 100 labels"
        table_data = table_data.head(100)

    full_list = md_truncated_table(table_data, 10, summary)

    return ["## Record Labels", "", full_list, "", img, ""]
