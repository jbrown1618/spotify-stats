import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.markdown import md_image
from utils.settings import figure_dpi, skip_figures
from utils.top_lists import get_term_length_description

def artist_rank_time_series(artist_uri: str, artist_name: str, absolute_path: str, relative_path: str) -> str:
    data = DataProvider().top_artists(artist_uris=[artist_uri])

    entry_counts_by_term = data.groupby('term')\
                                .agg({"index": "count"})\
                                .rename(columns={"index": "entry_count"})\
                                .reset_index()
    terms_with_sufficient_data = entry_counts_by_term[entry_counts_by_term['entry_count'] > 2]['term'].unique()

    data = data[data['term'].isin(terms_with_sufficient_data)]

    if len(data) == 0:
        return ''

    data['Date'] = data['as_of_date'].apply(lambda d: pd.to_datetime(d, format='%Y-%m-%d'))
    data['Term'] = data['term'].apply(get_term_length_description)
    data['Place'] = data['index'].apply(lambda x: -1 * x) # multiply by -1 to have lower places on top

    lowest_rank = data['index'].max()
    highest_rank = data['index'].min()

    y_max = -1 * (highest_rank - 1)
    y_min = -1 * (lowest_rank + 1)

    ticks = [-1, -10, -20, -30, -40, -50, -1 * lowest_rank, -1 * highest_rank]
    tick_labels = [str(-1 * i) for i in ticks]

    annotations = []
    for term in terms_with_sufficient_data:
        entries_for_term = data[data['term'] == term]

        max_date_for_term = entries_for_term['Date'].max()
        entry_at_max_date = entries_for_term[entries_for_term['Date'] == max_date_for_term].iloc[0]

        text = '  ' + entry_at_max_date['Term']
        coords = (entry_at_max_date['Date'], entry_at_max_date['Place'] - 0.15)

        for _, c in annotations:
            if c == coords:
                # Offset text for any annotations in the same location
                coords = (coords[0], coords[1] + 0.15)
    
        annotations.append((text, coords))

    data = data[['Date', 'Term', 'Place']]
    if not skip_figures():
        sns.set(rc = {"figure.figsize": (13,13) })
        sns.set_style('white')
        sns.set_palette('bright')

        ax = sns.lineplot(data=data, x='Date', y='Place', hue='Term', linewidth=3)

        plt.yticks(ticks=ticks, labels=tick_labels)
        plt.ylim([y_min, y_max])
        sns.despine(bottom=True)

        ax.get_legend().remove()
        for text, coords in annotations:
            plt.annotate(text, coords)

        ax.get_figure().savefig(absolute_path, dpi=figure_dpi())
        plt.clf()

    return md_image(f"Rank of {artist_name} over time", relative_path)
