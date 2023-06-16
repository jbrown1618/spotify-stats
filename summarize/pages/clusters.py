import os
import math
import typing
import pandas as pd
from sklearn.cluster import KMeans

from data.provider import DataProvider
from summarize.tables.tracks_table import tracks_table
from utils.track_features import comparison_scatter_plot, principal_component_analysis
from utils.markdown import md_truncated_table
from utils.path import ensure_directory

MIN_CLUSTERS = 3
MAX_CLUSTERS = 10
IDEAL_CLUSTER_SIZE = 50.0
MAX_CLUSTER_SIZE_RATIO = 10.0

def make_clusters_page(tracks: pd.DataFrame, description: str, path: str, figure_root_path: str):
    content = [f"# Clusters in {description}", ""]

    clusters, distances = get_clusters(tracks)

    if clusters is None:
        return

    content += clusters_scatterplot(clusters, path, figure_root_path)

    cluster_indices = list(clusters['cluster'].unique())
    cluster_indices.sort()

    for i in cluster_indices:
        cluster_track_uris = clusters[clusters['cluster'] == i].index
        distances_in_cluster = distances.loc[cluster_track_uris]
        distances_to_cluster_center = distances_in_cluster[i]
        content += cluster_section(i, cluster_track_uris, distances_to_cluster_center, path)

    with open(path, "w") as f:
        f.write("\n".join(content))


def clusters_scatterplot(clusters: pd.DataFrame, path: str, figure_root_path: str):
    current_page_dir = os.path.dirname(path)
    scatter_absolute_path = os.path.join(figure_root_path, 'clusters_scatter.png')
    ensure_directory(scatter_absolute_path)
    scatter_relative_path = os.path.relpath(scatter_absolute_path, current_page_dir)

    scatter = comparison_scatter_plot(
        DataProvider().tracks(clusters.index), 
        (clusters['cluster'] + 1).astype(str), 
        'Cluster', 
        scatter_absolute_path,
        scatter_relative_path
    )

    return [scatter, '']


def cluster_section(i: int, uris: pd.Series, distances_to_cluster_center: pd.Series, path: str):
    representative_track_uris = distances_to_cluster_center.sort_values(ascending=True).head(10).index
    tracks = DataProvider().tracks(uris=representative_track_uris)

    return [f'## Cluster #{i + 1}', '', f'{str(len(uris))} tracks', '', md_truncated_table(tracks_table(tracks, path))]


def get_clusters(tracks: pd.DataFrame) -> typing.Tuple[pd.DataFrame, pd.DataFrame]:
    tracks_data = DataProvider().ml_data(track_uris=tracks['track_uri'])

    if len(tracks_data) == 0:
        return None, None

    projected, components = principal_component_analysis(tracks_data, 5)
    clustering = get_clustering(projected)

    clusters_df = pd.DataFrame(data={'cluster': clustering.labels_}, index=tracks_data.index)

    distance_df = pd.DataFrame(data=clustering.transform(projected), index=tracks_data.index)
    # One col for the distance to each cluster

    return clusters_df, distance_df


def get_clustering(data: pd.DataFrame):    
    n = get_initial_cluster_count(data)

    clustering = None
    while n >= MIN_CLUSTERS and (clustering is None or is_bad_clustering(clustering)):
        clustering = KMeans(n_clusters=n, n_init='auto', random_state=0).fit(data)
        n -= 1

    return clustering


def get_initial_cluster_count(tracks: pd.DataFrame):
    return max(MIN_CLUSTERS, min(MAX_CLUSTERS, math.ceil(len(tracks) / IDEAL_CLUSTER_SIZE)))


def is_bad_clustering(clustering):
    counts = pd.Series(clustering.labels_).value_counts()
    largest = counts.iat[0]
    smallest = counts.iat[-1]

    return smallest * MAX_CLUSTER_SIZE_RATIO < largest
