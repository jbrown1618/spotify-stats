import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.fonts import change_fonts
from utils.markdown import md_image
from utils.settings import figure_dpi, skip_figures
from utils.top_lists import get_term_length_phrase

def artist_top_tracks_time_series(artist_uri: str, term: str, absolute_path: str, relative_path: str) -> str:
    artist_tracks = DataProvider().tracks(artist_uris={artist_uri})
    data = DataProvider().top_tracks(term=term, track_uris=artist_tracks['track_uri'].unique())

    entry_counts_by_track = data.groupby('track_uri')\
                                .agg({"index": "count"})\
                                .rename(columns={"index": "entry_count"})\
                                .reset_index()
    tracks_with_sufficient_data = entry_counts_by_track[entry_counts_by_track['entry_count'] > 2]['track_uri']

    data = data[data['track_uri'].isin(tracks_with_sufficient_data)]

    if len(data) == 0:
        return ''
    
    data = pd.merge(data, artist_tracks[['track_uri', 'track_name']], how='inner', on='track_uri')

    data['Date'] = data['as_of_date'].apply(lambda d: pd.to_datetime(d, format='%Y-%m-%d'))
    data['Track'] = data['track_name']
    data['Place'] = data['index'].apply(lambda x: -1 * x) # multiply by -1 to have lower places on top
    
    lowest_rank = data['index'].max()
    highest_rank = data['index'].min()

    y_max = -1 * (highest_rank - 1)
    y_min = -1 * (lowest_rank + 1)

    ticks = [-1, -10, -20, -30, -40, -50, -1 * lowest_rank, -1 * highest_rank]
    tick_labels = [str(-1 * i) for i in ticks]

    track_uris_in_data = data['track_uri'].unique()
    annotations = []
    for track_uri in track_uris_in_data:
        entries_for_track = data[data['track_uri'] == track_uri]
        max_date_for_track = entries_for_track['Date'].max()
        entry_at_max_date = entries_for_track[entries_for_track['Date'] == max_date_for_track].iloc[0]

        text = '  ' + entry_at_max_date['Track']
        coords = (entry_at_max_date['Date'], entry_at_max_date['Place'] - 0.15)
        annotations.append((text, coords))

    if not skip_figures():
        sns.set_theme(rc = {"figure.figsize": (13,13) })
        sns.set_style('white')
        sns.set_palette('bright')

        ax = sns.lineplot(data=data, x='Date', y='Place', hue='Track', linewidth=3)

        plt.yticks(ticks=ticks, labels=tick_labels)
        plt.ylim([y_min, y_max])
        sns.despine(bottom=True)

        ax.get_legend().remove()
        for text, coords in annotations:
            plt.annotate(text, coords)

        change_fonts(ax)
        ax.get_figure().savefig(absolute_path, dpi=figure_dpi())
        plt.clf()

    return md_image(f"Line chart of top tracks of {get_term_length_phrase(term)} over time", relative_path)
