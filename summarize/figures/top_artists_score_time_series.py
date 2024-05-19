import typing
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.fonts import change_fonts
from utils.markdown import md_image
from utils.settings import figure_dpi, skip_figures

top = 10
max_axis_range = 70

def top_artists_score_time_series(artist_uris: typing.Iterable[str], absolute_path: str, relative_path: str) -> str:
    artist_scores = DataProvider().artist_scores_over_time()

    artist_scores = artist_scores[artist_scores['artist_uri'].isin(artist_uris)]

    max_date = artist_scores['as_of_date'].max()
    current_top_artists = artist_scores[
        (artist_scores['as_of_date'] == max_date)
    ].head(top)['artist_uri']

    most_frequent_artists = artist_scores[artist_scores['artist_score_rank'] <= top]\
        .groupby('artist_uri')\
        .agg({'artist_score': 'count'})\
        .reset_index()\
        .rename(columns={'artist_score': 'appearances'})\
        .sort_values('appearances', ascending=False)\
        .head(10)['artist_uri']
    
    uris = {u for u in current_top_artists}.union({u for u in most_frequent_artists})

    artist_names = DataProvider().artists(uris=uris)[['artist_uri', 'artist_name']]
    data = artist_scores[artist_scores['artist_uri'].isin(uris)]
    data = pd.merge(data, artist_names, how="inner", on='artist_uri')

    if len(data) < 20:
        return ''

    data['Date'] = data['as_of_date'].apply(lambda d: pd.to_datetime(d, format='%Y-%m-%d'))
    data['Artist'] = data['artist_name']
    data['Place'] = data['artist_score_rank'].apply(lambda x: -1 * x) # multiply by -1 to have lower places on top

    lowest_rank = data['artist_score_rank'].max()
    highest_rank = data['artist_score_rank'].min()

    ticks = [-1, -10, -20, -30, -40, -50, -1 * lowest_rank, -1 * highest_rank]
    tick_labels = [str(-1 * i) for i in ticks]

    annotations = []
    current_ranks = []
    for artist_uri in uris:
        entries_for_artist = data[data['artist_uri'] == artist_uri]
        if len(entries_for_artist) == 0:
            continue

        max_date_for_track = entries_for_artist['Date'].max()
        entry_at_max_date = entries_for_artist[entries_for_artist['Date'] == max_date_for_track].iloc[0]

        text = '  ' + entry_at_max_date['Artist']
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

        ax = sns.lineplot(data=data, x='Date', y='Place', hue='Artist', linewidth=3)

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
