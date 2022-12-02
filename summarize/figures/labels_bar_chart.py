import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.util import md_image

def labels_bar_chart(tracks: pd.DataFrame, album_record_label: pd.DataFrame, absolute_path: str, relative_path: str):
    grouped = pd.merge(tracks, album_record_label, on="album_uri").groupby("album_standardized_label").agg({"track_uri": "count"}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "album_standardized_label"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "album_standardized_label": "Label"})
    
    fig_data = grouped[["Number of Tracks", "Label"]].head(30)
    if len(fig_data) == 0:
        return ""

    sns.set(rc = {"figure.figsize": (13,13) })
    ax = sns.barplot(data=fig_data, x="Number of Tracks", y="Label")
    ax.bar_label(ax.containers[0])
    ax.get_figure().savefig(absolute_path)
    plt.clf()

    return md_image(f"Bar chart of top {len(fig_data)} record labels", relative_path)
