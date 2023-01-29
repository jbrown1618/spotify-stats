import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from utils.markdown import md_table, md_image


audio_columns = ["audio_danceability", "audio_energy", "audio_speechiness", "audio_acousticness", "audio_instrumentalness", "audio_liveness", "audio_valence"]
labels = ["Danceable", "Energetic", "Speechy", "Acoustic", "Instrumental", "Live", "Happy"]
negated_labels = ["Not danceable", "Mellow", "Melodic", "Electronic", "Vocal", "Produced", "Sad"]


tracks_full_ = None
def set_tracks_full(tracks_full: pd.DataFrame):
    global tracks_full_
    tracks_full_ = tracks_full


def top_and_bottom_lists(tracks: pd.DataFrame):
    lines = []
    top_count = min(10, tracks.size / 2)

    for col, label in zip(audio_columns, labels):
        top_tracks = tracks.sort_values(by=[col, 'track_uri'], ascending=False)\
            .head(top_count)\
            .reset_index()\
            .apply(lambda track: f"{track['track_name']} ({track[col]})", axis=1)
        bottom_tracks = tracks.sort_values(by=[col, 'track_uri'], ascending=True)\
            .head(top_count)\
            .reset_index()\
            .apply(lambda track: f"{track['track_name']} ({track[col]})", axis=1)

        data = pd.DataFrame({
            f"{top_count} most {label} tracks": top_tracks,
            f"{top_count} least {label} tracks": bottom_tracks
        })
        
        lines += [md_table(data), ""]

    return lines


def audio_pairplot(tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    data = tracks[audio_columns].sample(n=500, random_state=0)
    sns.pairplot(data).savefig(absolute_path)
    plt.close("all")

    return md_image("Pairplot of audio features", relative_path)


def comparison_scatter_plot(tracks: pd.DataFrame, comparison_column, category_label: str, absolute_path: str, relative_path: str):
    projected, first_component, second_component = principal_component_analysis(tracks)

    x = projected[:,0]
    y = projected[:,1]
    x_label = label_for_eigenvector(first_component)
    y_label = label_for_eigenvector(second_component)

    data = {}

    if isinstance(comparison_column, str):
        categories = set(tracks[comparison_column].value_counts().head(10).index)
        data[category_label] = tracks[comparison_column].apply(lambda category: category if category in categories else "Other")
    else:
        categories = set(comparison_column.value_counts().head(10).index)
        data[category_label] = comparison_column.apply(lambda category: category if category in categories else "Other")

    data[x_label] = x
    data[y_label] = y
    data = pd.DataFrame(data)

    data = data[data[category_label] != "Other"]

    sns.set(rc = {"figure.figsize": (15,15) })
    ax = sns.scatterplot(data=data, x=x_label, y=y_label, hue=category_label)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    ax.get_figure().savefig(absolute_path)
    plt.close("all")

    return md_image(f"Comparison of {category_label}", relative_path)


def subset_scatter_plot(subset_label: str, track_uris, absolute_path, relative_path):
    projected, first_component, second_component = principal_component_analysis(tracks_full_)

    x = projected[:,0]
    y = projected[:,1]
    x_label = label_for_eigenvector(first_component)
    y_label = label_for_eigenvector(second_component)

    data = {}
    data[subset_label] = tracks_full_["track_uri"].apply(lambda uri: uri in track_uris)
    data[x_label] = x
    data[y_label] = y
    data = pd.DataFrame(data)

    sns.set(rc = {"figure.figsize": (15,15) })
    ax = sns.scatterplot(data=data, x=x_label, y=y_label, hue=subset_label)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    ax.get_figure().savefig(absolute_path)
    plt.close("all")

    return md_image(f"Songs in {subset_label} compared to all songs", relative_path)


def principal_component_analysis(tracks):
    mat = tracks[audio_columns].to_numpy()
    centered = center(mat)
    covariance = np.cov(centered, rowvar=False)

    eigenvalues, eigenvectors = np.linalg.eig(covariance)

    eigenvalue_indices = np.argsort(eigenvalues)[::-1]
    eigenvectors_sorted = eigenvectors[:,eigenvalue_indices]

    projection_mat = (eigenvectors_sorted[:2]).T

    projected = centered.dot(projection_mat)

    return (projected, eigenvectors_sorted[:,0], eigenvectors_sorted[:,1])


def project(tracks, first_component, second_component):
    mat = tracks[audio_columns].to_numpy()
    centered = center(mat)
    projection_mat = np.vstack((first_component, second_component)).T
    return centered.dot(projection_mat)


def center(X: np.ndarray):
    return X - np.mean(X, axis=0)


def label_for_eigenvector(eigenvector: np.ndarray):
    absolute_values = np.abs(eigenvector)
    signs = np.array([1 if val >= 0 else -1 for val in eigenvector])

    sorted_indices = np.argsort(absolute_values)[::-1]
    sorted_signs = signs[sorted_indices]

    label_parts = []
    for i in range(3):
        index = sorted_indices[i]
        sign = sorted_signs[i]
        label = labels[index] if sign == 1 else negated_labels[index]
        label_parts.append(label)

    return ", ".join(label_parts)
