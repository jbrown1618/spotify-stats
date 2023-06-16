import os
import math
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

def make_clusters_page(tracks: pd.DataFrame, description: str, path: str, figure_root_path: str):
    content = [f"# Clusters in {description}", ""]

    clusters = get_clusters(tracks)

    if clusters is None:
        return

    content += clusters_scatterplot(clusters, path, figure_root_path)

    for i in clusters['cluster'].unique():
        cluster = clusters[clusters['cluster'] == i].index
        content += cluster_section(i, cluster, path)

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

def cluster_section(i: int, uris: pd.Series, path: str):
    tracks = DataProvider().tracks(uris).head(10)

    return [f'## Cluster #{i + 1}', '', str(len(uris)), '', md_truncated_table(tracks_table(tracks, path))]


def get_clusters(tracks: pd.DataFrame) -> pd.Series:
    tracks_data = DataProvider().ml_data(track_uris=tracks['track_uri'])

    if len(tracks_data) == 0:
        return None, None

    clustering = get_clustering(tracks_data)

    clusters_df = pd.DataFrame(data={'cluster': clustering.labels_}, index=tracks_data.index)
    # centers_df = pd.DataFrame(data=clustering.cluster_centers_, columns=tracks_data.columns)

    # distance = clustering.transform(tracks_data)
    # One col for the distance to each cluster

    return clusters_df#, centers_df


def get_clustering(tracks_data: pd.DataFrame):
    projected, components = principal_component_analysis(tracks_data, 5)
    
    n = get_initial_cluster_count(projected)

    clustering = None
    while n >= MIN_CLUSTERS and (clustering is None or is_bad_clustering(clustering)):
        clustering = KMeans(n_clusters=n, n_init='auto', random_state=0).fit(projected)
        n -= 1

    print(pd.Series(clustering.labels_).value_counts())
    return clustering


def get_initial_cluster_count(tracks: pd.DataFrame):
    return max(MIN_CLUSTERS, min(MAX_CLUSTERS, math.ceil(len(tracks) / IDEAL_CLUSTER_SIZE)))


def is_bad_clustering(clustering):
    counts = pd.Series(clustering.labels_).value_counts()
    largest = counts.iat[0]
    smallest = counts.iat[-1]

    print(f"n: {len(counts)}, largest: {largest}, smallest: {smallest}")
    return smallest * 10 < largest
