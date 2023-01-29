import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.markdown import md_image
from utils.util import first

def artists_bar_chart(tracks: pd.DataFrame, track_artist_full: pd.DataFrame, absolute_path: str, relative_path: str):
    joined = pd.merge(track_artist_full, tracks, on="track_uri")
    grouped = joined.groupby("artist_uri").agg({
        "track_uri": "count", 
        "track_liked": "sum",
        "artist_name": first, 
        "artist_image_url": first
    }).reset_index()

    if len(grouped) < 3:
        return ""
    
    grouped = grouped.sort_values(by=["track_uri", "artist_uri"], ascending=False).head(30)

    all = grouped.rename(columns={"track_uri": "Number of Tracks", "artist_name": "Artist"})
    liked = grouped.rename(columns={"track_liked": "Number of Tracks", "artist_name": "Artist"})

    sns.set(rc = {"figure.figsize": (13,13) })
    sns.set_style('white')

    ax = sns.barplot(data=all, x="Number of Tracks", y="Artist", color="darkgray")
    sns.barplot(data=liked, x="Number of Tracks", y="Artist", color="limegreen")
    
    ax.bar_label(ax.containers[0])
    ax.bar_label(ax.containers[1])

    sns.despine(left=True)
    ax.get_figure().savefig(absolute_path)
    plt.clf()

    return md_image(f"Bar chart of top {len(all)} artists", relative_path)
