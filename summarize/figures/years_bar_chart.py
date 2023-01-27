import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils.markdown import md_image

def years_bar_chart(tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    grouped = tracks.groupby("album_release_year").agg({"track_uri": "count"}).reset_index()
    grouped = grouped.sort_values(by=["track_uri", "album_release_year"], ascending=False)
    grouped = grouped.rename(columns={"track_uri": "Number of Tracks", "album_release_year": "Year"})
    
    fig_data = grouped[["Number of Tracks", "Year"]]
    if len(fig_data) == 0:
        return ""

    ordered_years = grouped['Year'].to_list()
    ordered_years.sort()

    sns.set(rc = {"figure.figsize": (13,13) })
    ax = sns.barplot(data=fig_data, x="Year", y="Number of Tracks", order=ordered_years, color="green")
    ax.bar_label(ax.containers[0])
    plt.xticks(rotation=90)

    ax.get_figure().savefig(absolute_path)
    plt.clf()

    return md_image(f"Bar chart of number of songs by year", relative_path)
