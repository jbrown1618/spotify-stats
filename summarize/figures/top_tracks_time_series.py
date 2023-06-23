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

    lowest_rank = data['index'].max()
    highest_rank = 1

    y_max = -1 * (highest_rank - 1)
    y_min = -1 * min(lowest_rank + 1, 30)

    ticks = [-1, -10, -20, -30, -40, -50, -1 * lowest_rank]
    tick_labels = [str(-1 * i) for i in ticks]

    max_date = data['Date'].max()
    annotations = []
    for _, entry in data[data['Date'] == max_date].iterrows():
        text = '  ' + entry['Track']
        coords = (entry['Date'], entry['Place'] - 0.15)
        annotations.append((text, coords))

    if not skip_figures():
        sns.set(rc = {"figure.figsize": (13,13) })
        sns.set_style('white')
        sns.set_palette('bright')

        ax = sns.lineplot(data=data, x='Date', y='Place', hue='Track', linewidth=3)

        plt.yticks(ticks=ticks, labels=tick_labels)
        plt.ylim([y_min, y_max])
        sns.despine(bottom=True)

        ax.get_legend().remove()
        for text, coords in annotations:
            plt.annotate(text, coords)

        ax.get_figure().savefig(absolute_path)
        plt.clf()

    return md_image(f"Line chart of top tracks of {get_term_length_phrase(term)} over time", relative_path)
