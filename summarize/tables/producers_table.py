import pandas as pd

from data.provider import DataProvider
from utils.artist_relationship import related_artist_name, producer_credit_types
from utils.markdown import md_image
from utils.util import aggregate_to_unique_list, first


def producers_table(tracks: pd.DataFrame, relative_to: str):
    credits = DataProvider().track_credits(track_uris=tracks['track_uri'], credit_types=producer_credit_types)
    credits['credit_type'] = credits['credit_type'].apply(lambda t: t.capitalize())
    grouped = credits.groupby('artist_mbid').agg({
        'recording_mbid': lambda series: series.nunique(),
        'artist_image_url': first,
        'artist_name': first,
        'artist_mb_name': first,
        'artist_has_page': first,
        'artist_sort_name': first,
        'credit_type': aggregate_to_unique_list
    }).reset_index()

    grouped = grouped.sort_values(by="recording_mbid", ascending=False).head(100)
    if len(grouped) == 0:
        return pd.DataFrame({
            'Art':[], 'Producer':[], 'Tracks':[], 'Credit Types':[]
        })

    grouped['Producer'] = grouped.apply(lambda r: related_artist_name(r, relative_to), axis=1)
    grouped['Art'] = grouped['artist_image_url'].apply(lambda url: md_image("", url, 50))

    grouped = grouped.rename(columns={
        "recording_mbid": "Tracks",
        "credit_type": "Credit Types",
    })

    if grouped['Art'].apply(lambda a: len(a)).sum() > 0:
        return grouped[['Art', 'Producer', 'Tracks', 'Credit Types']]
    
    return grouped[['Art', 'Producer', 'Tracks', 'Credit Types']]
