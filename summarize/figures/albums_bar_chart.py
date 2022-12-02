import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.util import first, md_image

def albums_bar_chart(tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    grouped = tracks.groupby("album_uri").agg({"track_uri": "count", "album_name": first, "album_image_url": first}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "album_name"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "album_name": "Album"})
    
    fig_data = grouped[["Number of Tracks", "Album"]].head(30)
    if len(fig_data) == 0:
        return ""

    sns.set(rc = {"figure.figsize": (13,13) })
    ax = sns.barplot(data=fig_data, x="Number of Tracks", y="Album")
    ax.bar_label(ax.containers[0])
    ax.get_figure().savefig(absolute_path)
    plt.clf()
    
    return md_image(f"Bar chart of top {len(fig_data)} albums", relative_path)
