import pandas as pd
from summarize.figures.genres_bar_chart import genres_bar_chart
from utils.audio_features import audio_pairplot, comparison_scatter_plot, top_and_bottom_lists
from utils.path import errors_path, overview_genre_graph_path, overview_genres_scatterplot_path, overview_playlists_scatterplot_path, pairplot_path, playlist_path, overview_path
from utils.settings import output_dir
from utils.util import md_image, md_link, spotify_link

def make_overview(playlists: pd.DataFrame, playlist_track: pd.DataFrame, tracks_full: pd.DataFrame, track_genre: pd.DataFrame):
    print("Generating Overview")

    readme = []

    readme += title("jbrown1618")
    readme += byline()
    readme += liked_songs()
    readme += errors()
    readme += playlists_section(playlists, playlist_track, tracks_full)
    readme += genres_section(tracks_full, track_genre)
    readme += audio_features_section(tracks_full)

    with open(overview_path(), "w") as f:
        f.write("\n".join(readme))


def title(user: str):
    return [f"# Spotify Summary for {user}", ""]


def byline():
    return [f"Generated by {md_link('jbrown1618/spotify-stats', 'https://github.com/jbrown1618/spotify-stats')}", ""]


def liked_songs():
    return ["## Liked Songs", md_link("Liked Songs", playlist_path("Liked Songs", output_dir()))]


def errors():
    return ['## Possible organizational errors', md_link("Possible organizational errors", errors_path(output_dir()))]


def playlists_section(playlists: pd.DataFrame, playlist_track: pd.DataFrame, tracks_full: pd.DataFrame):
    track_counts = pd\
        .merge(left=playlists, right=playlist_track, left_on="playlist_uri", right_on="playlist_uri", how="inner")\
        .groupby("playlist_uri")\
        .agg({"track_uri": "count"})\
        .reset_index()

    display_playlists = pd\
        .merge(left=playlists, right=track_counts, left_on="playlist_uri", right_on="playlist_uri", how="inner")

    display_playlists["🔗"] = display_playlists["playlist_uri"].apply(lambda uri: spotify_link(uri))
    display_playlists["Name"] = display_playlists["playlist_name"].apply(lambda name: md_link(name, playlist_path(name, output_dir())))
    display_playlists["Number of Songs"] = display_playlists["track_uri"]
    display_playlists["Art"] = display_playlists["playlist_image_url"].apply(lambda src: md_image("", src, 50))

    display_playlists = display_playlists[["Art", "Name", "Number of Songs", "🔗"]]

    display_playlists.sort_values(by="Name", inplace=True)

    table = display_playlists.to_markdown(index=False)

    playlists_sorted_by_track_count = track_counts.sort_values(by="track_uri", ascending=False)["playlist_uri"]
    main_playlist_col = tracks_full["track_uri"].apply(lambda track_uri: get_main_playlist(track_uri, playlist_track, playlists, playlists_sorted_by_track_count))
    scatter = comparison_scatter_plot(tracks_full, main_playlist_col, "Playlist", overview_playlists_scatterplot_path(), overview_playlists_scatterplot_path(output_dir()))
    
    return ["## Playlists", "", table, "", scatter, ""]


def genres_section(tracks: pd.DataFrame, track_genre: pd.DataFrame):
    img = genres_bar_chart(tracks, track_genre, overview_genre_graph_path(), overview_genre_graph_path(output_dir()))
    main_genre_col = tracks["track_uri"].apply(lambda track_uri: get_main_genre(track_uri, track_genre))
    scatter = comparison_scatter_plot(tracks, main_genre_col, "Genre", overview_genres_scatterplot_path(), overview_genres_scatterplot_path(output_dir()))

    return ["## Genres", "", img, "", scatter, ""]


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



def audio_features_section(tracks_full):
    return [
        "## Audio Features", 
        "", 
        audio_pairplot(tracks_full, pairplot_path(), pairplot_path(output_dir())), 
        ""
    ] + top_and_bottom_lists(tracks_full)