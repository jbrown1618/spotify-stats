import typing
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.markdown import md_image
from utils.settings import figure_dpi, skip_figures
from utils.top_lists import get_term_length_phrase

min_data_points_per_track = 3

def top_tracks_time_series(term: str, top: int, absolute_path: str, relative_path: str) -> str:
    track_uris = get_included_track_uris(term, top)

    data = DataProvider().top_tracks(term=term, track_uris=track_uris)
    if len(data) < 20:
        return ""
    
    tracks = DataProvider().tracks(uris=track_uris)
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

    annotations = []
    for track_uri in track_uris:
        entries_for_track = data[data['track_uri'] == track_uri]
        max_date_for_track = entries_for_track['Date'].max()
        entry_at_max_date = entries_for_track[entries_for_track['Date'] == max_date_for_track].iloc[0]

        text = '  ' + entry_at_max_date['Track']
        coords = (entry_at_max_date['Date'], entry_at_max_date['Place'] - 0.15)
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

        ax.get_figure().savefig(absolute_path, dpi=figure_dpi())
        plt.clf()

    return md_image(f"Line chart of top tracks of {get_term_length_phrase(term)} over time", relative_path)


def get_included_track_uris(term: str, top: int) -> typing.Iterable[str]:
    dp = DataProvider()

    # include tracks currently in the top N if they have enough data
    current_top_track_uris = dp.top_tracks(term=term, top=top, min_occurrences=min_data_points_per_track, current=True)['track_uri'].unique()

    # include the tracks that have appeared most frequently in the top N
    top_tracks = dp.top_tracks(top=top, term=term)
    grouped = top_tracks.groupby('track_uri').agg({'as_of_date': 'count'}).reset_index().sort_values('as_of_date', ascending=False)
    most_frequent_uris = grouped.head(top)['track_uri'].unique()

    return {u for u in current_top_track_uris}.union({u for u in most_frequent_uris})
