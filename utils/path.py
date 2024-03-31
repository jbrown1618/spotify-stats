import os
import glob
import typing
from utils.settings import output_dir
from utils.util import file_name_friendly


persistent_data_sources = {
    'top_tracks',
    'top_artists'
}


def clear_markdown():
    clear_contents(artists_path())
    clear_contents(playlists_path())
    clear_contents(labels_path())
    clear_contents(genres_path())
    clear_contents(images_path())


def clear_contents(path: str, exclude: typing.Iterable[str] = []):
    files = glob.glob(f'{path}/*')
    for f in files:
        if any([exclusion_path in f for exclusion_path in exclude]):
            continue

        if os.path.isfile(f):
            os.remove(f)
        else:
            clear_contents(f, exclude)


def images_path(relative_to=None):
    return relative_to_path("images", relative_to)


def overview_path(relative_to=None):
    return relative_to_path("README.md", relative_to)


def overview_audio_features_path(relative_to=None):
    return relative_to_path("audio_features.md", relative_to)


def overview_clusters_path(relative_to=None):
    return relative_to_path("clusters.md", relative_to)


def overview_clusters_figure_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "clusters"),
        relative_to
    )


def overview_playlists_scatterplot_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "playlists_comparison.png"),
        relative_to
    )


def overview_genre_graph_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "genres.png"), 
        relative_to
    )


def overview_genres_scatterplot_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "genres_comparison.png"),
        relative_to
    )


def overview_artist_graph_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "artists.png"),
        relative_to
    )


def overview_artists_scatterplot_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "artists_comparison.png"),
        relative_to
    )


def overview_top_artists_time_series_path(term: str, relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "top_artists" ,f"{term}.png"),
        relative_to
    )


def overview_top_tracks_time_series_path(term: str, relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "top_tracks" ,f"{term}.png"),
        relative_to
    )


def overview_label_graph_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "labels.png"),
        relative_to
    )


def overview_producers_graph_path(relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "overview",
            "producers.png"
        ),
        relative_to
    )


def overview_audio_features_figure_path(relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "overview",
            "audio_features"
        ),
        relative_to
    )


def errors_path(relative_to=None):
    return relative_to_path("errors.md", relative_to)


def artists_path():
    return os.path.join(output_dir(), "artists")


def artist_path(artist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "artists",
            file_name_friendly(artist_name)
        ), 
        relative_to
    )


def artist_overview_path(artist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "artists",
            file_name_friendly(artist_name),
            "overview.md"
        ), 
        relative_to
    )


def artist_audio_features_path(artist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "artists",
            file_name_friendly(artist_name),
            "audio_features.md"
        ), 
        relative_to
    )


def artist_audio_features_chart_path(artist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "artists",
            file_name_friendly(artist_name),
            "audio_features"
        ),
        relative_to
    )


def artist_clusters_path(artist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "artists",
            file_name_friendly(artist_name),
            "clusters",
            "overview.md"
        ), 
        relative_to
    )


def artist_clusters_figure_path(artist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "artists",
            file_name_friendly(artist_name),
            "clusters"
        ),
        relative_to
    )


def artist_rank_time_series_path(artist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "artists",
            file_name_friendly(artist_name),
            "rank_time_series.png"
        ),
        relative_to
    )


def artist_top_tracks_time_series_path(artist_name: str, term: str, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "artists",
            file_name_friendly(artist_name),
            f"track_rank_time_series_{term}.png"
        ),
        relative_to
    )

def artist_producers_graph_path(artist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "artists",
            file_name_friendly(artist_name),
            "producers.png"
        ),
        relative_to
    )

def playlists_path():
    return os.path.join(output_dir(), "playlists")


def playlist_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "playlists",
            file_name_friendly(playlist_name)
        ), 
        relative_to
    )


def playlist_overview_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "playlists",
            file_name_friendly(playlist_name),
            "overview.md"
        ), 
        relative_to
    )


def playlist_audio_features_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "playlists",
            file_name_friendly(playlist_name),
            "audio_features.md"
        ), 
        relative_to
    )


def playlist_audio_features_figure_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "audio_features"
        ),
        relative_to
    )


def playlist_clusters_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "playlists",
            file_name_friendly(playlist_name),
            "clusters",
            "overview.md"
        ), 
        relative_to
    )


def playlist_clusters_figure_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "clusters"
        ),
        relative_to
    )


def playlist_year_path(playlist_name, year: str, relative_to=None):
    return relative_to_path(
        os.path.join(
            "playlists",
            file_name_friendly(playlist_name),
            f"{year}.md"
        ), 
        relative_to
    )


def playlist_producers_graph_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "producers.png"
        ),
        relative_to
    )


def playlist_artist_graph_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "artists.png"
        ),
        relative_to
    )


def playlist_label_graph_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "labels.png"
        ),
        relative_to
    )


def playlist_album_graph_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "albums.png"
        ),
        relative_to
    )


def playlist_genre_graph_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "genres.png"
        ),
        relative_to
    )


def playlist_years_graph_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "years.png"
        ),
        relative_to
    )


def playlist_artist_comparison_scatterplot_path(playlist_name: str, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "artists_comparison.png"
        ), 
        relative_to
    )

def playlist_top_tracks_time_series_path(playlist_name: str, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "playlists",
            file_name_friendly(playlist_name),
            "top_tracks_time_series.png"
        ), 
        relative_to
    )

def labels_path():
    return os.path.join(output_dir(), "labels")


def label_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "labels",
            file_name_friendly(label_name)
        ), 
        relative_to
    )


def label_overview_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "labels",
            file_name_friendly(label_name),
            "overview.md"
        ), 
        relative_to
    )


def label_audio_features_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "labels",
            file_name_friendly(label_name),
            "audio_features.md"
        ), 
        relative_to
    )


def label_audio_features_chart_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "labels",
            file_name_friendly(label_name),
            "audio_features"
        ),
        relative_to
    )


def label_artist_graph_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "labels",
            file_name_friendly(label_name),
            "artists.png"
        ),
        relative_to
    )


def label_album_graph_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "labels",
            file_name_friendly(label_name),
            "albums.png"
        ),
        relative_to
    )


def label_genre_graph_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "labels",
            file_name_friendly(label_name),
            "genres.png"
        ),
        relative_to
    )


def label_producers_graph_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "labels",
            file_name_friendly(label_name),
            "producers.png"
        ),
        relative_to
    )


def label_clusters_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "labels",
            file_name_friendly(label_name),
            "clusters",
            "overview.md"
        ), 
        relative_to
    )


def label_clusters_figure_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "labels",
            file_name_friendly(label_name),
            "clusters"
        ),
        relative_to
    )


def genres_path():
    return os.path.join(output_dir(), "genres")


def genre_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "genres",
            file_name_friendly(genre_name)
        ), 
        relative_to
    )


def genre_overview_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "genres",
            file_name_friendly(genre_name),
            "overview.md"
        ), 
        relative_to
    )


def genre_artist_graph_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "genres",
            file_name_friendly(genre_name),
            "artists.png"
        ),
        relative_to
    )


def genre_label_graph_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "genres",
            file_name_friendly(genre_name),
            "labels.png"
        ),
        relative_to
    )


def genre_album_graph_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "genres",
            file_name_friendly(genre_name),
            "albums.png"
        ),
        relative_to
    ) 


def genre_artist_comparison_scatterplot_path(genre_name: str, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "genres",
            file_name_friendly(genre_name),
            "artists_comparison.png"
        ), 
        relative_to
    )


def genre_producers_graph_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "genres",
            file_name_friendly(genre_name),
            "producers.png"
        ),
        relative_to
    )


def genre_years_graph_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "genres",
            file_name_friendly(genre_name),
            "years.png"
        ),
        relative_to
    )


def genre_audio_features_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "genres",
            file_name_friendly(genre_name),
            "audio_features.md"
        ), 
        relative_to
    )


def genre_audio_features_chart_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "genres",
            file_name_friendly(genre_name),
            "audio_features"
        ),
        relative_to
    )


def genre_clusters_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "genres",
            file_name_friendly(genre_name),
            "clusters",
            "overview.md"
        ), 
        relative_to
    )


def genre_clusters_figure_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            "genres",
            file_name_friendly(genre_name),
            "clusters"
        ),
        relative_to
    )


def producer_path(producer_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "producers",
            file_name_friendly(producer_name)
        ), 
        relative_to
    )


def producer_overview_path(producer_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "producers",
            file_name_friendly(producer_name),
            "overview.md"
        ), 
        relative_to
    )


def pairplot_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "audio", "audio_pairplot.png"), 
        relative_to
    )


def data_path(source=None, table_name=None, relative_to=None):
    if table_name is  None:
        return relative_to_path(os.path.join("data", "spotify"), relative_to)

    return relative_to_path(
        os.path.join(
            "data",
            source,
            table_name + ".csv"
        ), 
        relative_to
    )


def persistent_data_path(source, table_name: str, year: str, relative_to=None):
    return relative_to_path(
        os.path.join(
            "data",
            source,
            table_name,
            year + ".csv"
        ),
        relative_to
    )


def musicbrainz_data_path(table_name: str, relative_to=None):
    return relative_to_path(
        os.path.join(
            "data",
            "musicbrainz",
            table_name + ".csv"
        ),
        relative_to
    )
        

def relative_to_path(destination, relative_to=None):
    path_from_cwd = os.path.join(output_dir(), destination)

    if relative_to is None:
        ensure_directory(path_from_cwd)
        return path_from_cwd
    else:
        return os.path.relpath(
            os.path.abspath(path_from_cwd),
            os.path.abspath(relative_to)
        )


def ensure_directory(path: str):
    dir = os.path.dirname(path)
    if os.path.isdir(dir):
        return

    os.makedirs(dir)
