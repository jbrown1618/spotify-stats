import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.markdown import md_image
from utils.settings import skip_figures
from utils.top_lists import get_term_length_phrase

def top_tracks_time_series(term: str, top: int, absolute_path: str, relative_path: str) -> str:
    current_top_track_uris = DataProvider().top_tracks(term=term, top=top, current=True)['track_uri'].unique()
    data = DataProvider().top_tracks(term=term, track_uris=current_top_track_uris)
    tracks = DataProvider().tracks(uris=current_top_track_uris)
    data = pd.merge(data, tracks[['track_uri', 'track_name']], how='inner', on='track_uri')

    data['Date'] = data['as_of_date'].apply(lambda d: pd.to_datetime(d, format='%Y-%m-%d'))
    data['Track'] = data['track_name']
    data['Place'] = data['index'].apply(lambda x: -1 * x) # multiply by -1 to have lower places on top

    ticks = [-1, -10, -20, -30, -40, -50]
    tick_labels = [str(-1 * i) for i in ticks]

    if not skip_figures():
        sns.set(rc = {"figure.figsize": (13,13) })
        sns.set_style('white')

        ax = sns.lineplot(data=data, x='Date', y='Place', hue='Track')

        plt.xticks(rotation=90)
        plt.yticks(ticks=ticks, labels=tick_labels)
        sns.despine(bottom=True)
        ax.get_figure().savefig(absolute_path)
        plt.clf()

    return md_image(f"Line chart of top tracks of {get_term_length_phrase(term)} over time", relative_path)


