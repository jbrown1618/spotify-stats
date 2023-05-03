import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from data.provider import DataProvider

from utils.markdown import md_image
from utils.settings import skip_figures

class AudioFeature:
     def __init__(self, column, label, adjective, negated_adjective, type, categories=None, normalized=False):
        self.column = column
        self.label = label
        self.adjective = adjective
        self.negated_adjective = negated_adjective
        self.type = type
        self.categories = categories
        self.normalized = normalized


audio_features = [
    AudioFeature(
        column='audio_danceability',
        label='Danceability',
        adjective='Danceable',
        negated_adjective='Not danceable',
        type='numeric',
        normalized=True
    ),
    AudioFeature(
        column='audio_energy',
        label='Energy',
        adjective='Energetic',
        negated_adjective='Mellow',
        type='numeric',
        normalized=True
    ),
    AudioFeature(
        column='audio_speechiness',
        label='Speechiness',
        adjective='Speechy',
        negated_adjective='Melodic',
        type='numeric',
        normalized=True
    ),
    AudioFeature(
        column='audio_acousticness',
        label='Acousticness',
        adjective='Acoustic',
        negated_adjective='Electronic',
        type='numeric',
        normalized=True
    ),
    AudioFeature(
        column='audio_instrumentalness',
        label='Instrumentalness',
        adjective='Instrumental',
        negated_adjective='Vocal',
        type='numeric',
        normalized=True
    ),
    AudioFeature(
        column='audio_liveness',
        label='Liveness',
        adjective='Live',
        negated_adjective='Produced',
        type='numeric',
        normalized=True
    ),
    AudioFeature(
        column='audio_valence',
        label='Valence',
        adjective='Happy',
        negated_adjective='Sad',
        type='numeric',
        normalized=True
    ),
    AudioFeature(
        column='audio_tempo',
        label='Tempo',
        adjective='Fast',
        negated_adjective='Slow',
        type='numeric',
        normalized=False
    )
]


def audio_pairplot(tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    numeric_audio_columns = [
        feature.column 
        for feature in audio_features 
        if feature.type == 'numeric'
    ]
    
    data = tracks[numeric_audio_columns]
    if len(data) > 200:
        data = data.sample(n=200, random_state=0)

    if not skip_figures():
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


    if not skip_figures():
        sns.set(rc = {"figure.figsize": (15,15) })
        ax = sns.scatterplot(data=data, x=x_label, y=y_label, hue=category_label)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        ax.get_figure().savefig(absolute_path)
        plt.close("all")

    return md_image(f"Comparison of {category_label}", relative_path)


def subset_scatter_plot(subset_label: str, track_uris, absolute_path, relative_path):
    dp = DataProvider()
    projected, first_component, second_component = principal_component_analysis(dp.tracks())

    x = projected[:,0]
    y = projected[:,1]
    x_label = label_for_eigenvector(first_component)
    y_label = label_for_eigenvector(second_component)

    data = {}
    data[subset_label] = dp.tracks()["track_uri"].apply(lambda uri: uri in track_uris)
    data[x_label] = x
    data[y_label] = y
    data = pd.DataFrame(data)

    if not skip_figures():
        sns.set(rc = {"figure.figsize": (15,15) })
        ax = sns.scatterplot(data=data, x=x_label, y=y_label, hue=subset_label)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        ax.get_figure().savefig(absolute_path)
        plt.close("all")

    return md_image(f"Songs in {subset_label} compared to all songs", relative_path)


def principal_component_analysis(tracks):
    numeric_audio_columns = [
        feature.column 
        for feature in audio_features 
        if feature.type == 'numeric' and feature.normalized
    ]
    mat = tracks[numeric_audio_columns].to_numpy()
    centered = center(mat)
    covariance = np.cov(centered, rowvar=False)

    eigenvalues, eigenvectors = np.linalg.eig(covariance)

    eigenvalue_indices = np.argsort(eigenvalues)[::-1]
    eigenvectors_sorted = eigenvectors[:,eigenvalue_indices]

    projection_mat = (eigenvectors_sorted[:2]).T

    projected = centered.dot(projection_mat)

    return (projected, eigenvectors_sorted[:,0], eigenvectors_sorted[:,1])


def project(tracks, first_component, second_component):
    numeric_audio_columns = [
        feature.column 
        for feature in audio_features 
        if feature.type == 'numeric' and feature.normalized
    ]
    mat = tracks[numeric_audio_columns].to_numpy()
    centered = center(mat)
    projection_mat = np.vstack((first_component, second_component)).T
    return centered.dot(projection_mat)


def center(X: np.ndarray):
    return X - np.mean(X, axis=0)


def label_for_eigenvector(eigenvector: np.ndarray):
    numeric_audio_adjectives = [
        feature.adjective 
        for feature in audio_features 
        if feature.type == 'numeric' and feature.normalized
    ]

    numeric_audio_negated_adjectives = [
        feature.negated_adjective 
        for feature in audio_features 
        if feature.type == 'numeric' and feature.normalized
    ]

    absolute_values = np.abs(eigenvector)
    signs = np.array([1 if val >= 0 else -1 for val in eigenvector])

    sorted_indices = np.argsort(absolute_values)[::-1]
    sorted_signs = signs[sorted_indices]

    label_parts = []
    for i in range(3):
        index = sorted_indices[i]
        sign = sorted_signs[i]
        label = numeric_audio_adjectives[index] if sign == 1 else numeric_audio_negated_adjectives[index]
        label_parts.append(label)

    return ", ".join(label_parts)
