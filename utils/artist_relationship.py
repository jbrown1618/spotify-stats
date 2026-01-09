import pandas as pd
from utils.markdown import md_link
from utils.path import artist_overview_path, producer_overview_path


# Credit types for songwriting and production work (excludes performance credits)
producer_credit_types = {
    'songwriter', 
    'lyricist', 
    'producer', 
    'arranger', 
    'sound', 
    'mastering',
    'audio director',
    'video director',
    'publishing'
}

def relationship_description(relationship_row, relative_to_path):
    return relationship_phrase(relationship_row) + " " + mb_artist_display_name(relationship_row, relative_to_path)


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
    

def mb_artist_display_name(relationship_row, relative_to_path):
    if 'artist_name' in relationship_row and not pd.isna(relationship_row['artist_name']):
        if relationship_row['artist_has_page']:
            return md_link(relationship_row['artist_name'], artist_overview_path(relationship_row['artist_name'], relative_to_path))
        else:
            return relationship_row['artist_name']
        
    name = mb_artist_name(relationship_row['artist_mb_name'], relationship_row['artist_sort_name'])
    if 'producer_has_page' in relationship_row and relationship_row['producer_has_page']:
        return md_link(name, producer_overview_path(name, relative_to_path))
    
    return name


def related_artist_plain_name(relationship_row):
    if not pd.isna(relationship_row['artist_name']):
        return relationship_row['artist_name']
    
    return mb_artist_name(relationship_row['artist_mb_name'], relationship_row['artist_sort_name'])


def mb_artist_name(mb_name, sort_name):
    if not mb_name.isascii():
        return f"{mb_name} ({sort_name})"
    
    return mb_name
