import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.markdown import md_image

def genres_bar_chart(tracks: pd.DataFrame, track_genre: pd.DataFrame, absolute_path: str, relative_path: str):
    cols_in_genre = track_genre.columns.difference(tracks.columns).to_list() + ["track_uri"]
    track_genre_subset = pd.merge(tracks, track_genre[cols_in_genre], on="track_uri")
    grouped = track_genre_subset.groupby("genre").agg({
        "track_uri": "count",
        "track_liked": "sum"
    }).reset_index()
    
    if len(grouped) == 0:
        return ""

    grouped = grouped.sort_values(by=["track_uri", "genre"], ascending=False).head(30)

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
