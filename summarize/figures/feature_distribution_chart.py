import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.audio_features import AudioFeature
from utils.markdown import md_image
from utils.settings import skip_figures

def feature_distribution_chart(feature: AudioFeature, tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    feature_data = tracks[feature.column]
    if len(feature_data) > 200:
        feature_data = feature_data.sample(200, random_state=0)

    if not skip_figures():
        sns.set(rc = {"figure.figsize": (7,13) })
        sns.set_style('white')

        ax = sns.kdeplot(feature_data, fill=True, color="limegreen")

        plt.xlabel(feature.label)
        sns.despine(left=True)
        plt.ylabel("")
        plt.yticks([])
        ax.get_figure().savefig(absolute_path)
        plt.clf()

    return md_image(f"Bar chart of number of songs by year", relative_path)