import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.fonts import change_fonts
from utils.markdown import md_image
from utils.settings import figure_dpi, skip_figures
from utils.util import first

def albums_bar_chart(tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    grouped = tracks.groupby("album_uri").agg({
        "track_uri": "count",
        "track_liked": "sum",
        "album_short_name": first, 
        "album_image_url": first
    }).reset_index()

    if len(grouped) < 3:
        return ""
    
    grouped = grouped.sort_values(by=["track_uri", "track_liked", "album_short_name"], ascending=False).head(30)

    all = grouped.rename(columns={"track_uri": "Number of Tracks", "album_short_name": "Album"})
    liked = grouped.rename(columns={"track_liked": "Number of Tracks", "album_short_name": "Album"})
    
    if not skip_figures():
        sns.set(rc = {"figure.figsize": (13,13) })
        sns.set_style('white')

        ax = sns.barplot(data=all, x="Number of Tracks", y="Album", color="darkgray")
        sns.barplot(data=liked, x="Number of Tracks", y="Album", color="limegreen")

        ax.bar_label(ax.containers[0])
        ax.bar_label(ax.containers[1])

        sns.despine(left=True)
        change_fonts(ax)
        ax.get_figure().savefig(absolute_path, dpi=figure_dpi())
        plt.clf()
    
    return md_image(f"Bar chart of top {len(all)} albums", relative_path)
