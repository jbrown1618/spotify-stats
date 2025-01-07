import re
import pandas as pd

album_index_regex = re.compile(r"\d+(st|nd|rd|th)( mini)? album")
ending_parenthetical_regex = re.compile(r"\((.+)\)$")
actual_name_in_quotes_regex = re.compile(r"(.+)\"(.+)\"")
disposable_keywords = {"remaster", "deluxe", "soundtrack", "standard", "bonus", "stereo", "version"}

def short_name(full_name: str):
    if pd.isna(full_name):
        return full_name
    
    if ' - ' in full_name:
        parts = full_name.split(' - ', 1)
        main = parts[0].strip()
        suffix = parts[1].strip()
        if is_disposable(suffix):
            return main

    search = ending_parenthetical_regex.search(full_name)
    if search is not None:
        index = search.start()
        parenthetical = search.group(1)
        if is_disposable(parenthetical):
            return full_name[:index]
        
    search = actual_name_in_quotes_regex.search(full_name)
    if search is not None:
        opening = search.group(1)
        if is_disposable(opening):
            return search.group(2) # The contents of the quotes

    return full_name



def is_disposable(segment: str):
    segment = segment.lower()

    for keyword in disposable_keywords:
        if keyword in segment:
            return True

    if album_index_regex.search(segment):
        return True

    return False
