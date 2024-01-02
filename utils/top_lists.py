top_list_terms = [
    'short_term',
    'medium_term',
    'long_term'
]

graphable_top_list_terms = [
    'long_term',
    'medium_term'
]

def get_term_length_description(term):
    if term == 'short_term':
        return 'Last month'
    
    if term == 'medium_term':
        return 'Last 6 months'
    
    if term == 'long_term':
        return 'All time'
    

def get_term_length_phrase(term):
    if term == 'short_term':
        return 'the last month'
    
    if term == 'medium_term':
        return 'the last 6 months'
    
    if term == 'long_term':
        return 'all time'