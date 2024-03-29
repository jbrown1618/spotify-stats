top_list_terms = [
    'short_term',
    'medium_term',
    'long_term'
]

graphable_top_list_terms_for_tracks = [
    'long_term',
    'medium_term',
    'on_repeat'
]

graphable_top_list_terms_for_artists = [
    'long_term',
    'medium_term'
]

def get_term_length_description(term):
    if term == 'on_repeat':
        return 'On repeat'
    
    if term == 'short_term':
        return 'Last month'
    
    if term == 'medium_term':
        return 'Last 6 months'
    
    if term == 'long_term':
        return 'All time'
    

def get_term_length_phrase(term):
    if term == 'on_repeat':
        return 'the On Repeat playlist'
    
    if term == 'short_term':
        return 'the last month'
    
    if term == 'medium_term':
        return 'the last 6 months'
    
    if term == 'long_term':
        return 'all time'