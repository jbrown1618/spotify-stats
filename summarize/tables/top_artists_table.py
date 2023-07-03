import pandas as pd

from data.provider import DataProvider
from utils.artist import get_artist_link
from utils.markdown import empty_header, md_image
from utils.settings import output_dir
from utils.top_lists import get_term_length_description

def top_artists_table():
    artists = DataProvider().artists()
    top_artists = DataProvider().top_artists(current=True)
    
    top_artists_with_data = pd.merge(top_artists, artists, on="artist_uri")
    short = top_artists_with_data[top_artists_with_data['term'] == 'short_term']
    medium = top_artists_with_data[top_artists_with_data['term'] == 'medium_term']
    long = top_artists_with_data[top_artists_with_data['term'] == 'long_term']
    table_data = pd.merge(short, medium, on="index", how="outer")
    table_data = pd.merge(table_data, long, on="index", how="outer")

    table_data["Place"] = table_data["index"]
    table_data[empty_header(1)] = table_data.apply(lambda row: display_image(row, "_x"), axis=1)
    table_data[get_term_length_description('short_term')] = table_data.apply(lambda row: display_artist(row, "_x"), axis=1)
    table_data[empty_header(2)] = table_data.apply(lambda row: display_image(row, "_y"), axis=1)
    table_data[get_term_length_description('medium_term')] = table_data.apply(lambda row: display_artist(row, "_y"), axis=1)
    table_data[empty_header(3)] = table_data.apply(lambda row: display_image(row, ""), axis=1)
    table_data[get_term_length_description('long_term')] = table_data.apply(lambda row: display_artist(row, ""), axis=1)

    table_data.sort_values(by="Place", ascending=True, inplace=True)

    return table_data[[
        'Place', 
        empty_header(1), get_term_length_description('short_term'), 
        empty_header(2), get_term_length_description('medium_term'), 
        empty_header(3), get_term_length_description('long_term')
    ]]


def display_image(row: pd.Series, suffix: str):
    if pd.isna(row["artist_image_url" + suffix]):
        return ''
    
    return md_image(row["artist_name" + suffix], row["artist_image_url" + suffix], 50)


def display_artist(row: pd.Series, suffix: str):
    return get_artist_link(row, output_dir(), suffix)
