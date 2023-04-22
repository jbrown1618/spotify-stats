import os
import glob
from utils.settings import output_dir
from utils.util import file_name_friendly


def clear_data():
    clear_contents(data_path())


def clear_markdown():
    clear_contents(artists_path())
    clear_contents(playlists_path())
    clear_contents(labels_path())
    clear_contents(genres_path())
    clear_contents(images_path())


def clear_contents(path: str):
    files = glob.glob(f'{path}/*')
    for f in files:
        if os.path.isfile(f):
            os.remove(f)
        else:
            clear_contents(f)


def images_path(relative_to=None):
    return relative_to_path("images", relative_to)


def overview_path(relative_to=None):
    return relative_to_path("README.md", relative_to)


def overview_audio_features_path(relative_to=None):
    return relative_to_path("audio_features.md", relative_to)


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


def overview_label_graph_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "overview", "labels.png"),
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


def playlist_tracks_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "playlists",
            file_name_friendly(playlist_name),
            "tracks.md"
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


def playlist_year_path(playlist_name, year: str, relative_to=None):
    return relative_to_path(
        os.path.join(
            "playlists",
            file_name_friendly(playlist_name),
            f"{year}.md"
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


def genre_audio_features_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "genres",
            file_name_friendly(genre_name),
            "audio_features.md"
        ), 
        relative_to
    )


def genre_tracks_path(genre_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "genres",
            file_name_friendly(genre_name),
            "tracks.md"
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


def pairplot_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "audio", "audio_pairplot.png"), 
        relative_to
    )


def data_path(table_name=None, relative_to=None):
    if table_name is  None:
        return relative_to_path("data", relative_to)

    return relative_to_path(
        os.path.join(
            "data",
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
