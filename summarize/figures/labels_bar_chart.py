import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.markdown import md_image

def labels_bar_chart(tracks: pd.DataFrame, album_record_label: pd.DataFrame, absolute_path: str, relative_path: str):
    grouped = pd.merge(tracks, album_record_label, on="album_uri").groupby("album_standardized_label").agg({
        "track_uri": "count",
        "track_liked": "sum"
    }).reset_index()

    if len(grouped) < 3:
        return ""

    grouped = grouped.sort_values(by=["track_uri", "track_liked", "album_standardized_label"], ascending=False).head(30)
    
    all = grouped.rename(columns={"track_uri": "Number of Tracks", "album_standardized_label": "Label"})
    liked = grouped.rename(columns={"track_liked": "Number of Tracks", "album_standardized_label": "Label"})
    
    sns.set(rc = {"figure.figsize": (13,13) })
    sns.set_style('white')

    ax = sns.barplot(data=all, x="Number of Tracks", y="Label", color="darkgray")
    sns.barplot(data=liked, x="Number of Tracks", y="Label", color="limegreen")

    ax.bar_label(ax.containers[0])
    ax.bar_label(ax.containers[1])

    sns.despine(left=True)
    ax.get_figure().savefig(absolute_path)
    plt.clf()

    return md_image(f"Bar chart of top {len(all)} record labels", relative_path)
