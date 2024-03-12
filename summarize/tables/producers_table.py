import pandas as pd

from data.provider import DataProvider
from utils.artist_relationship import mb_artist_display_name, producer_credit_types
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
        'producer_has_page': first,
        'credit_type': aggregate_to_unique_list
    }).reset_index()

    grouped = grouped.sort_values(by="recording_mbid", ascending=False).head(100)
    if len(grouped) == 0:
        return pd.DataFrame({
            'Art':[], 'Producer':[], 'Tracks':[], 'Credit Types':[]
        })

    grouped['Producer'] = grouped.apply(lambda r: mb_artist_display_name(r, relative_to), axis=1)
    grouped['Art'] = grouped['artist_image_url'].apply(lambda url: md_image("", url, 50))

    grouped = grouped.rename(columns={
        "recording_mbid": "Tracks",
        "credit_type": "Credit Types",
    })

    if grouped['Art'].apply(lambda a: len(a)).sum() > 0:
        return grouped[['Art', 'Producer', 'Tracks', 'Credit Types']]
    
    return grouped[['Art', 'Producer', 'Tracks', 'Credit Types']]


def co_producers_table(producer_mbid: str, relative_to: str):
    credits_for_producer = DataProvider().track_credits(artist_mbids={producer_mbid}, credit_types=producer_credit_types)
    track_uris = credits_for_producer['track_uri']
    all_credits_for_tracks = DataProvider().track_credits(track_uris=track_uris, credit_types=producer_credit_types)
    other_credits: pd.DataFrame = all_credits_for_tracks[all_credits_for_tracks['artist_mbid'] != producer_mbid]
    
    # one per artist per track
    grouped = other_credits.groupby(['artist_mbid', 'track_uri']).agg({
        'artist_mb_name': first,
        'artist_sort_name': first,
        'artist_image_url': first,
        'producer_has_page': first,
    }).reset_index()

    # counts per artist
    grouped = grouped.groupby(['artist_mbid']).agg({
        'artist_mb_name': first,
        'artist_sort_name': first,
        'artist_image_url': first,
        'producer_has_page': first,
        'track_uri': 'count'
    }).reset_index()

    grouped['Producer'] = grouped.apply(lambda row: mb_artist_display_name(row, relative_to), axis=1)

    display = grouped.rename(columns={
        'artist_mb_name': 'Producer',
        'track_uri': 'Tracks'
    })[['Producer', 'Tracks']]

    display = display.sort_values(by=['Tracks'], ascending=False)

    return display


def production_credits_table(artist_mbid: str = None, artist_uri: str = None, relative_to: str = None) -> pd.DataFrame:
    production_credits = DataProvider().track_credits(
        artist_uri=artist_uri, 
        include_aliases=True, 
        credit_types=producer_credit_types
    ) if artist_uri is not None else DataProvider().track_credits(
        artist_mbids={artist_mbid}, 
        include_aliases=True, 
        credit_types=producer_credit_types
    )

    members = DataProvider().group_members(artist_uri)
    if members is not None and len(members) > 0:
        member_credits = DataProvider().track_credits(
            artist_mbids=members["artist_mbid"],
            include_aliases=True, 
            credit_types=producer_credit_types)
        
        if len(member_credits) > 0:
            production_credits = pd.concat([production_credits, member_credits])

    if len(production_credits) == 0:
        return None

    production_credits['credit_type'] = production_credits['credit_type'].apply(lambda t: t.capitalize())
    production_credits['display_name'] = production_credits.apply(lambda r: mb_artist_display_name(r, relative_to), axis=1)

    display = production_credits.groupby('recording_mbid').agg({
        'album_image_url': first,
        'album_name': first,
        'album_release_date': first,
        'track_name': first,
        'track_uri': first,
        'display_name': aggregate_to_unique_list,
        'credit_type': aggregate_to_unique_list,
    }).reset_index().sort_values(['album_release_date', 'track_uri'])

    display['Art'] = display['album_image_url'].apply(lambda url: md_image("", url, 50))
    display = display.rename(columns={
        'track_name': 'Track',
        'album_name': 'Album',
        'credit_type': 'Credit Types',
        'display_name': 'Members'
    })

    if members is not None and len(members) > 0:
        display = display[['Art', 'Track', 'Members', 'Credit Types']]
    else:
        display = display[['Art', 'Track', 'Credit Types']]

    return display
