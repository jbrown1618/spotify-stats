import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.fonts import change_fonts
from utils.markdown import md_image
from utils.settings import figure_dpi, skip_figures

top = 10

def top_tracks_score_time_series(tracks: pd.DataFrame, absolute_path: str, relative_path: str) -> str:
    track_scores = DataProvider().track_scores_over_time()

    track_scores = track_scores[track_scores['track_uri'].isin(tracks['track_uri'])]

    max_date = track_scores['as_of_date'].max()
    current_top_tracks = track_scores[
        (track_scores['as_of_date'] == max_date)
    ].head(top)['track_uri']

    most_frequent_tracks = track_scores[track_scores['track_score_rank'] <= top]\
        .groupby('track_uri')\
        .agg({'track_score': 'count'})\
        .reset_index()\
        .rename(columns={'track_score': 'appearances'})\
        .sort_values('appearances', ascending=False)\
        .head(10)['track_uri']
    
    track_uris = {u for u in current_top_tracks}.union({u for u in most_frequent_tracks})

    track_names = DataProvider().tracks(uris=track_uris)[['track_uri', 'track_name']]
    data = track_scores[track_scores['track_uri'].isin(track_uris)]
    data = pd.merge(data, track_names, how="inner", on='track_uri')

    if len(data) < 20:
        return ''

    data['Date'] = data['as_of_date'].apply(lambda d: pd.to_datetime(d, format='%Y-%m-%d'))
    data['Track'] = data['track_name']
    data['Place'] = data['track_score_rank'].apply(lambda x: -1 * x) # multiply by -1 to have lower places on top

    lowest_rank = data['track_score_rank'].max()
    highest_rank = data['track_score_rank'].min()

    y_max = -1 * (highest_rank - 1)
    y_min = -1 * (lowest_rank + 1)

    ticks = [-1, -10, -20, -30, -40, -50, -1 * lowest_rank, -1 * highest_rank]
    tick_labels = [str(-1 * i) for i in ticks]

    annotations = []
    for track_uri in track_uris:
        entries_for_track = data[data['track_uri'] == track_uri]
        if len(entries_for_track) == 0:
            continue

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

    return md_image('Track score ranking over time', relative_path)
