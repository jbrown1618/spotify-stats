from genericpath import isfile
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


def readme_path(relative_to=None):
    return relative_to_path("README.md", relative_to)


def errors_path(relative_to=None):
    return relative_to_path("errors.md", relative_to)


def artists_path():
    return os.path.join(output_dir(), "artists")


def artist_path(artist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "artists",
            file_name_friendly(artist_name) + ".md"
        ), 
        relative_to
    )


def playlists_path():
    return os.path.join(output_dir(), "playlists")


def playlist_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "playlists",
            file_name_friendly(playlist_name) + ".md"
        ), 
        relative_to
    )


def playlist_tracks_path(playlist_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "playlists",
            file_name_friendly(playlist_name) + "_tracks.md"
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


def labels_path():
    return os.path.join(output_dir(), "labels")


def label_path(label_name, relative_to=None):
    return relative_to_path(
        os.path.join(
            "labels",
            file_name_friendly(label_name) + ".md"
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


def pairplot_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "audio", "audio_pairplot.png"), 
        relative_to
    )


def playlists_comparison_scatterplot_path(relative_to=None):
    return relative_to_path(
        os.path.join("images", "audio", "playlist_comparison.png"),
        relative_to
    )


def playlists_artist_comparison_scatterploy_path(playlist_name: str, relative_to=None):
    return relative_to_path(
        os.path.join(
            "images",
            file_name_friendly(playlist_name),
            "artists_comparison.png"
        ), 
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
