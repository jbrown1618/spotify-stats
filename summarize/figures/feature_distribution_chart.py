import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.audio_features import AudioFeature
from utils.markdown import md_image

def feature_distribution_chart(feature: AudioFeature, tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    sns.set(rc = {"figure.figsize": (7,13) })
    sns.set_style('white')

    ax = sns.kdeplot(tracks[feature.column], fill=True, color="limegreen")

    plt.xlabel(feature.label)
    sns.despine(left=True)
    plt.ylabel("")
    plt.yticks([])
    ax.get_figure().savefig(absolute_path)
    plt.clf()

    return md_image(f"Bar chart of number of songs by year", relative_path)