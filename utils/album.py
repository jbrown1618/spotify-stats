import re
import pandas as pd

album_index_regex = re.compile(r"the \d+(st|nd|rd|th)( mini)? album")
ending_parenthetical_regex = re.compile(r"\((.+)\)$")
disposable_keywords = {"remaster", "deluxe", "soundtrack", "standard", "bonus", "stereo"}

def short_album_name(album_name: str):
    if pd.isna(album_name):
        return album_name
    
    if ' - ' in album_name:
        parts = album_name.split(' - ', 1)
        main = parts[0].strip()
        suffix = parts[1].strip()
        if is_disposable(suffix):
            return main

    search = ending_parenthetical_regex.search(album_name)
    if search is not None:
        index = search.start()
        parenthetical = search.group(1)
        if is_disposable(parenthetical):
            return album_name[:index]

    return album_name



def is_disposable(segment: str):
    segment = segment.lower()

    for keyword in disposable_keywords:
        if keyword in segment:
            return True

    if album_index_regex.match(segment):
        return True

    return False
