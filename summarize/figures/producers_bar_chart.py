import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from data.provider import DataProvider

from utils.artist_relationship import producer_credit_types, related_artist_plain_name
from utils.markdown import md_image
from utils.settings import skip_figures
from utils.util import first

def producers_bar_chart(tracks: pd.DataFrame, absolute_path: str, relative_path: str):
    credits = DataProvider().track_credits(track_uris=tracks['track_uri'], credit_types=producer_credit_types)
    grouped = credits.groupby('artist_mbid').agg({
        'recording_mbid': lambda series: series.nunique(),
        'artist_name': first,
        'artist_mb_name': first,
        'artist_sort_name': first,
    }).reset_index()

    grouped['display_name'] = grouped.apply(lambda r: related_artist_plain_name(r), axis=1)

    grouped = grouped.sort_values(by=["recording_mbid", 'display_name'], ascending=False)
    if len(grouped) < 3:
        return ''
    
    grouped = grouped.rename(columns={
        'recording_mbid': 'Tracks',
        'display_name': 'Producer'
    })[['Tracks', 'Producer']]

    if not skip_figures():
        sns.set(rc = {"figure.figsize": (13,13) })
        sns.set_style('white')

        ax = sns.barplot(data=grouped, x="Tracks", y="Producer", color="limegreen")

        sns.despine(left=True)
        ax.get_figure().savefig(absolute_path)
        plt.clf()

    return md_image(f"Bar chart of top {len(grouped)} producers", relative_path)
