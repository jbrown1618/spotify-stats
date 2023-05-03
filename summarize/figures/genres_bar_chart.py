import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.markdown import md_image

def genres_bar_chart(tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    dp = DataProvider()
    
    grouped = pd.merge(tracks, dp.track_genre(), on="track_uri").groupby("genre").agg({
        "track_uri": "count",
        "track_liked": "sum"
    }).reset_index()
    
    if len(grouped) < 3:
        return ""

    grouped = grouped.sort_values(by=["track_uri", "track_liked", "genre"], ascending=False).head(30)

    all = grouped.rename(columns={"track_uri": "Number of Tracks", "genre": "Genre"})
    liked = grouped.rename(columns={"track_liked": "Number of Tracks", "genre": "Genre"})    

    sns.set(rc = {"figure.figsize": (13,13) })
    sns.set_style('white')
    
    ax = sns.barplot(data=all, x="Number of Tracks", y="Genre", color="darkgray")
    sns.barplot(data=liked, x="Number of Tracks", y="Genre", color="limegreen")
    
    ax.bar_label(ax.containers[0])
    ax.bar_label(ax.containers[1])

    sns.despine(left=True)
    ax.get_figure().savefig(absolute_path)
    plt.clf()
    
    return md_image(f"Bar chart of top {len(all)} genres", relative_path)
