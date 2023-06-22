import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.markdown import md_image
from utils.settings import skip_figures

def top_artists_time_series(term: str, top: int, absolute_path: str, relative_path: str) -> str:
    current_top_artist_uris = DataProvider().top_artists(term=term, top=top, current=True)['artist_uri'].unique()
    data = DataProvider().top_artists(term=term, artist_uris=current_top_artist_uris)
    artists = DataProvider().artists(uris=current_top_artist_uris)
    data = pd.merge(data, artists[['artist_uri', 'artist_name']], how='inner', on='artist_uri')

    data['Date'] = data['as_of_date'].apply(lambda d: pd.to_datetime(d, format='%Y-%m-%d'))
    data['Artist'] = data['artist_name']
    data['Place'] = data['index'].apply(lambda x: -1 * x) # multiply by -1 to have lower places on top

    ticks = [-1, -10, -20, -30, -40, -50]
    tick_labels = [str(-1 * i) for i in ticks]

    if not skip_figures():
        sns.set(rc = {"figure.figsize": (13,13) })
        sns.set_style('white')

        ax = sns.lineplot(data=data, x='Date', y='Place', hue='Artist')

        plt.xticks(rotation=90)
        plt.yticks(ticks=ticks, labels=tick_labels)
        sns.despine(bottom=True)
        ax.get_figure().savefig(absolute_path)
        plt.clf()

    return md_image(f"Line chart of top artists in a {term} window over time", relative_path)


