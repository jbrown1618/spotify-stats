import typing

from routes.utils import to_json
from data.provider import DataProvider


def artists_payload(track_uris: typing.Iterable[str], min_date, max_date):
    if track_uris is None or len(track_uris) == 0:
        return {}

    dp = DataProvider()
    artists = dp.artists(track_uris=track_uris, start_date=min_date, end_date=max_date)
    return to_json(artists, 'artist_uri')


# Columns to include for artist relationship data
RELATIONSHIP_COLUMNS = [
    'artist_mbid', 'artist_mb_name', 'artist_sort_name', 
    'relationship_type', 'relationship_direction', 
    'artist_uri', 'artist_name', 'artist_image_url'
]


def artist_credits_payload(artist_uri: str):
    dp = DataProvider()
    
    result = {}
    
    # Get songwriting/producing credits
    credits = dp.artist_credits(artist_uri)
    if credits is not None and len(credits) > 0:
        result['credits'] = to_json(credits)
    
    # Get aliases
    aliases = dp.artist_aliases(artist_uri)
    if aliases is not None and len(aliases) > 0:
        result['aliases'] = to_json(aliases[RELATIONSHIP_COLUMNS])
    
    # Get group members (for groups)
    members = dp.group_members(artist_uri)
    if members is not None and len(members) > 0:
        result['members'] = to_json(members)
    
    # Get groups (for individuals)
    groups = dp.artist_groups(artist_uri)
    if groups is not None and len(groups) > 0:
        result['groups'] = to_json(groups[RELATIONSHIP_COLUMNS])
    
    # Get subgroups (for groups)
    subgroups = dp.artist_subgroups(artist_uri)
    if subgroups is not None and len(subgroups) > 0:
        result['subgroups'] = to_json(subgroups[RELATIONSHIP_COLUMNS])
    
    return result