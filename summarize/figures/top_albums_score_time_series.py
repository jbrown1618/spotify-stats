import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from data.provider import DataProvider
from utils.fonts import change_fonts
from utils.markdown import md_image
from utils.ranking import album_ranks_over_time
from utils.settings import figure_dpi, skip_figures
from utils.tick_labels import get_ticks

top = 10
max_axis_range = 70

def top_albums_score_time_series(tracks: pd.DataFrame, absolute_path: str, relative_path: str) -> str:
    album_ranks = album_ranks_over_time()

    album_ranks = album_ranks[album_ranks['album_uri'].isin(tracks['album_uri'])]

    max_date = album_ranks['as_of_date'].max()
    current_top_albums = album_ranks[
        (album_ranks['as_of_date'] == max_date)
    ].head(top)['album_uri']

    most_frequent_albums = album_ranks[album_ranks['album_rank'] <= top]\
        .groupby('album_uri')\
        .agg({'album_rank': 'count'})\
        .reset_index()\
        .rename(columns={'album_rank': 'appearances'})\
        .sort_values('appearances', ascending=False)\
        .head(10)['album_uri']
    
    album_uris = {u for u in current_top_albums}.union({u for u in most_frequent_albums})

    album_names = DataProvider().albums(uris=album_uris)[['album_uri', 'album_short_name']]
    data = album_ranks[album_ranks['album_uri'].isin(album_uris)]
    data = pd.merge(data, album_names, how="inner", on='album_uri')

    if len(data) < 20:
        return ''

    data['Date'] = data['as_of_date'].apply(lambda d: pd.to_datetime(d, format='%Y-%m-%d'))
    data['Album'] = data['album_short_name']
    data['Place'] = data['album_rank'].apply(lambda x: -1 * x) # multiply by -1 to have lower places on top

    lowest_rank = data['album_rank'].max()
    highest_rank = data['album_rank'].min()


    annotations = []
    current_ranks = []
    for album_uri in album_uris:
        entries_for_album = data[data['album_uri'] == album_uri]
        if len(entries_for_album) == 0:
            continue

        max_date_for_album = entries_for_album['Date'].max()
        entry_at_max_date = entries_for_album[entries_for_album['Date'] == max_date_for_album].iloc[0]

        text = '  ' + entry_at_max_date['Album']
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

    ticks = get_ticks(y_max - 1, y_min)
    tick_labels = [str(-1 * i) for i in ticks]

    if not skip_figures():
        sns.set_theme(rc = {"figure.figsize": (13,13) })
        sns.set_style('white')
        sns.set_palette('bright')

        ax = sns.lineplot(data=data, x='Date', y='Place', hue='Album', linewidth=3)

        plt.yticks(ticks=ticks, labels=tick_labels)
        plt.ylim([y_min, y_max])
        sns.despine(bottom=True)

        ax.get_legend().remove()
        for text, coords in annotations:
            plt.annotate(text, coords)

        change_fonts(ax)
        ax.get_figure().savefig(absolute_path, dpi=figure_dpi())
        plt.clf()

    return md_image('Album ranking over time', relative_path)
