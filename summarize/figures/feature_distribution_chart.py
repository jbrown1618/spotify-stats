import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.track_features import TrackFeature
from utils.markdown import md_image
from utils.settings import skip_figures

def feature_distribution_chart(feature: TrackFeature, tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    liked_sample = DataProvider().liked_tracks_sample()

    feature_data = tracks[feature.column]
    liked_data = liked_sample[feature.column]

    if len(feature_data) > 200:
        feature_data = feature_data.sample(200, random_state=0)

    if not skip_figures():
        sns.set(rc = {"figure.figsize": (7,13) })
        sns.set_style('white')

        ax = sns.kdeplot(feature_data, fill=True, color="darkgray")
        sns.kdeplot(liked_data, fill=True, color="limegreen")

        plt.legend(['These tracks', 'Liked tracks'])

        plt.xlabel(feature.label)
        sns.despine(left=True)
        plt.ylabel("")
        plt.yticks([])
        ax.get_figure().savefig(absolute_path)
        plt.clf()

    return md_image(f"Distribution of {feature.label} compared to all liked tracks", relative_path)