import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.util import md_image

def genres_bar_chart(tracks: pd.DataFrame, track_genre: pd.DataFrame, absolute_path: str, relative_path: str):
    track_genre_subset = pd.merge(tracks, track_genre, on="track_uri")[["genre", "track_uri", "genre_has_page"]]
    grouped = track_genre_subset.groupby("genre").agg({"track_uri": "count"}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "genre"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "genre": "Genre"})
    
    fig_data = grouped[["Number of Tracks", "Genre"]].head(30)
    if len(fig_data) == 0:
        return ""

    sns.set(rc = {"figure.figsize": (13,13) })
    ax = sns.barplot(data=fig_data, x="Number of Tracks", y="Genre")
    ax.bar_label(ax.containers[0])
    ax.get_figure().savefig(absolute_path)
    plt.clf()
    
    return md_image(f"Bar chart of top {len(fig_data)} genres", relative_path)
