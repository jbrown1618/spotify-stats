import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.markdown import md_image

def years_bar_chart(tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    grouped = tracks.groupby("album_release_year").agg({
        "track_uri": "count",
        "track_liked": "sum"
    }).reset_index()

    if len(grouped) < 3:
        return ""

    grouped = grouped.sort_values(by=["track_uri", "album_release_year"], ascending=False)
    
    all = grouped.rename(columns={"track_uri": "Number of Tracks", "album_release_year": "Year"})
    liked = grouped.rename(columns={"track_liked": "Number of Tracks", "album_release_year": "Year"})

    ordered_years = grouped['album_release_year'].to_list()
    ordered_years.sort()

    sns.set(rc = {"figure.figsize": (13,13) })
    sns.set_style('white')

    ax = sns.barplot(data=all, x="Year", y="Number of Tracks", order=ordered_years, color="darkgray")
    sns.barplot(data=liked, x="Year", y="Number of Tracks", order=ordered_years, color="limegreen")

    ax.bar_label(ax.containers[0])
    ax.bar_label(ax.containers[1])

    plt.xticks(rotation=90)
    sns.despine(bottom=True)
    ax.get_figure().savefig(absolute_path)
    plt.clf()

    return md_image(f"Bar chart of number of songs by year", relative_path)
