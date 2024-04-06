import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.fonts import change_fonts
from utils.markdown import md_image
from utils.settings import figure_dpi, skip_figures

def labels_bar_chart(tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    dp = DataProvider()
    labels = dp.labels(track_uris=tracks['track_uri'])

    if len(labels) < 3:
        return ""

    labels = labels.sort_values(by=["label_track_count", "label_track_liked_count", "album_standardized_label"], ascending=False)\
        .head(30)
    
    all = labels.rename(columns={"label_track_count": "Number of Tracks", "album_standardized_label": "Label"})
    liked = labels.rename(columns={"label_track_liked_count": "Number of Tracks", "album_standardized_label": "Label"})
    

    if not skip_figures():
        sns.set_theme(rc = {"figure.figsize": (13,13) })
        sns.set_style('white')

        ax = sns.barplot(data=all, x="Number of Tracks", y="Label", color="darkgray")
        sns.barplot(data=liked, x="Number of Tracks", y="Label", color="limegreen")

        ax.bar_label(ax.containers[0])
        ax.bar_label(ax.containers[1])

        sns.despine(left=True)
        change_fonts(ax)
        ax.get_figure().savefig(absolute_path, dpi=figure_dpi())
        plt.clf()

    return md_image(f"Bar chart of top {len(all)} record labels", relative_path)
