import pandas as pd

from data.provider import DataProvider
from utils.markdown import md_image
from utils.util import aggregate_to_unique_list, first
from utils.artist_relationship import producer_credit_types, related_artist_name


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
    production_credits['display_name'] = production_credits.apply(lambda r: related_artist_name(r, relative_to), axis=1)

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