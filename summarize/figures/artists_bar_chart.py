import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.util import first, md_image

def artists_bar_chart(tracks: pd.DataFrame, track_artist_full: pd.DataFrame, absolute_path: str, relative_path: str):
    joined = pd.merge(track_artist_full, tracks, on="track_uri")
    grouped = joined.groupby("artist_uri").agg({"track_uri": "count", "artist_name": first, "artist_image_url": first}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "artist_uri"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "artist_name": "Artist"})
    
    fig_data = grouped[["Number of Tracks", "Artist"]].head(30)
    if len(fig_data) == 0:
        return ""

    sns.set(rc = {"figure.figsize": (13,13) })
    ax = sns.barplot(data=fig_data, x="Number of Tracks", y="Artist")
    ax.bar_label(ax.containers[0])
    ax.get_figure().savefig(absolute_path)
    plt.clf()

    return md_image(f"Bar chart of top {len(fig_data)} artists", relative_path)
