import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.fonts import change_fonts
from utils.markdown import md_image
from utils.ranking import track_ranks_over_time
from utils.settings import figure_dpi, skip_figures

top = 10
max_axis_range = 70

def top_tracks_score_time_series(tracks: pd.DataFrame, absolute_path: str, relative_path: str) -> str:
    track_ranks = track_ranks_over_time()

    track_ranks = track_ranks[track_ranks['track_uri'].isin(tracks['track_uri'])]

    max_date = track_ranks['as_of_date'].max()
    current_top_tracks = track_ranks[
        (track_ranks['as_of_date'] == max_date)
    ].head(top)['track_uri']

    most_frequent_tracks = track_ranks[track_ranks['track_rank'] <= top]\
        .groupby('track_uri')\
        .agg({'track_rank': 'count'})\
        .reset_index()\
        .rename(columns={'track_rank': 'appearances'})\
        .sort_values('appearances', ascending=False)\
        .head(10)['track_uri']
    
    track_uris = {u for u in current_top_tracks}.union({u for u in most_frequent_tracks})

    track_names = DataProvider().tracks(uris=track_uris)[['track_uri', 'track_name']]
    data = track_ranks[track_ranks['track_uri'].isin(track_uris)]
    data = pd.merge(data, track_names, how="inner", on='track_uri')

    if len(data) < 20:
        return ''

    data['Date'] = data['as_of_date'].apply(lambda d: pd.to_datetime(d, format='%Y-%m-%d'))
    data['Track'] = data['track_name']
    data['Place'] = data['track_rank'].apply(lambda x: -1 * x) # multiply by -1 to have lower places on top

    lowest_rank = data['track_rank'].max()
    highest_rank = data['track_rank'].min()

    ticks = [-1, -10, -20, -30, -40, -50, -1 * lowest_rank, -1 * highest_rank]
    tick_labels = [str(-1 * i) for i in ticks]

    annotations = []
    current_ranks = []
    for track_uri in track_uris:
        entries_for_track = data[data['track_uri'] == track_uri]
        if len(entries_for_track) == 0:
            continue

        max_date_for_track = entries_for_track['Date'].max()
        entry_at_max_date = entries_for_track[entries_for_track['Date'] == max_date_for_track].iloc[0]

        text = '  ' + entry_at_max_date['Track']
        rank = entry_at_max_date['Place']
        date = entry_at_max_date['Date']

        coords = (date, rank - 0.15)
        annotations.append((text, coords))
        current_ranks.append(-1 * rank)

    min_annotation_space = None
    last = None
    current_ranks.sort()
    for rank in current_ranks:
        if last is not None:
            annotation_space = rank - last
            if min_annotation_space is None or annotation_space < min_annotation_space:
                min_annotation_space = annotation_space
        last = rank
    
    y_max = -1 * (highest_rank - 1)
    y_min = -1 * (lowest_rank + 1)

    lowest_current_rank = max(current_ranks)
    if min_annotation_space is not None and y_max - y_min > max_axis_range * min_annotation_space:
        # Can we cut everything off from the bottom? If so, do
        new_min = y_max - max_axis_range * min_annotation_space
        if new_min < -1 * lowest_current_rank:
            y_min = new_min
        else:  
            # We can't make it totally legible without cutting off labels, so do as much as we can
            y_min = -1 * (lowest_current_rank + 1)

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
