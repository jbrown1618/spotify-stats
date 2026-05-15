import pandas as pd
import sqlalchemy

from routes.utils import to_json
from routes.pagination import paginate_df, ARTIST_SORT_COLUMNS
from data.filters import filtered_connection
from data.provider import DataProvider
from data.query import query_text


def artists_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        artists = pd.read_sql_query(
            sqlalchemy.text(query_text('select_artists')),
            conn,
            params={
                "filter_artists": False,
                "artist_uris": ('EMPTY',),
                "filter_mbids": False,
                "mbids": ('EMPTY',),
                "wrapped_start_date": params["wrapped_start_date"],
                "wrapped_end_date": params["wrapped_end_date"],
            }
        )
    if artists.empty:
        return {}

    paginated = paginate_df(artists, filters, ARTIST_SORT_COLUMNS, "Most streams")
    if paginated is not None:
        return paginated

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