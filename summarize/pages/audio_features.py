import os
import pandas as pd

from summarize.figures.feature_distribution_chart import feature_distribution_chart
from utils.audio_features import AudioFeature, audio_features
from utils.markdown import md_table
from utils.path import ensure_directory


def make_audio_features_page(tracks: pd.DataFrame, description: str, path: str, figure_root_path: str):
    content = [f"# Audio Features for {description}", ""]

    for feature in audio_features:
        content += feature_section(feature, tracks, path, figure_root_path)

    with open(path, "w") as f:
        f.write("\n".join(content))


def feature_section(feature: AudioFeature, tracks: pd.DataFrame, path: str, figure_root_path: str):
    content = [f"## {feature.label}", ""]
    current_page_dir = os.path.dirname(path)

    if feature.type == 'numeric':
        dist_absolute_path = os.path.join(figure_root_path, feature.column, 'distribution.png')
        ensure_directory(dist_absolute_path)
        dist_relative_path = os.path.relpath(dist_absolute_path, current_page_dir)
        content += [feature_distribution_chart(feature, tracks, dist_absolute_path, dist_relative_path), ""]
        content += top_and_bottom_lists(feature, tracks)

    return content


def top_and_bottom_lists(feature: AudioFeature, tracks: pd.DataFrame):    
    top_count = min(10, tracks.size / 2)

    col = feature.column

    top_tracks = tracks.sort_values(by=[col, 'track_uri'], ascending=False)\
        .head(top_count)\
        .reset_index()\
        .apply(lambda track: f"{track['track_name']} ({track[col]})", axis=1)
    
    bottom_tracks = tracks.sort_values(by=[col, 'track_uri'], ascending=True)\
        .head(top_count)\
        .reset_index()\
        .apply(lambda track: f"{track['track_name']} ({track[col]})", axis=1)

    data = pd.DataFrame({
        f"{top_count} most {feature.adjective} tracks": top_tracks,
        f"{top_count} least {feature.adjective} tracks": bottom_tracks
    })
    
    return [md_table(data), ""]
