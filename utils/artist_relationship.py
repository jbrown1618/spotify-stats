import pandas as pd
from utils.markdown import md_link
from utils.path import artist_overview_path


def relationship_description(relationship_row, relative_to_path):
    return relationship_phrase(relationship_row) + " " + related_artist_name(relationship_row, relative_to_path)

def relationship_phrase(relationship_row):
    relationship = relationship_row['relationship_type']
    direction = relationship_row['relationship_direction']

    if relationship == 'member of band':
        return 'is a member of' if direction == 'forward' else 'has member'
    
    if relationship == 'is person':
        return 'is also known as'
    
    if relationship == 'artist rename':
        return 'is later known as' if direction == 'forward' else 'was formerly known as'
    
    if relationship == 'subgroup':
        return 'is a subgroup of' if direction == 'forward' else 'has the subgroup'
    

def related_artist_name(relationship_row, relative_to_path):
    if not pd.isna(relationship_row['artist_name']):
        return md_link(relationship_row['artist_name'], artist_overview_path(relationship_row['artist_name'], relative_to_path)) if relationship_row['artist_has_page'] else relationship_row['artist_name']
    
    if not relationship_row['name'].isascii():
        return f"{relationship_row['name']} ({relationship_row['sort_name']})"
    
    return relationship_row['name']