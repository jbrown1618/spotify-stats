import pandas as pd
from utils.artist import get_artist_link

from utils.markdown import empty_header, md_image
from utils.settings import output_dir

def top_artists_table(top_artists: pd.DataFrame, artists: pd.DataFrame):
    top_artists_with_data = pd.merge(top_artists, artists, on="artist_uri")
    short = top_artists_with_data[top_artists_with_data['term'] == 'short_term']
    medium = top_artists_with_data[top_artists_with_data['term'] == 'medium_term']
    long = top_artists_with_data[top_artists_with_data['term'] == 'long_term']
    table_data = pd.merge(short, medium, on="index", how="outer")
    table_data = pd.merge(table_data, long, on="index", how="outer")

    table_data["Place"] = table_data["index"]
    table_data[empty_header(1)] = table_data.apply(lambda row: display_image(row, "_x"), axis=1)
    table_data['Last month'] = table_data.apply(lambda row: display_artist(row, "_x"), axis=1)
    table_data[empty_header(2)] = table_data.apply(lambda row: display_image(row, "_y"), axis=1)
    table_data['Last 6 months'] = table_data.apply(lambda row: display_artist(row, "_y"), axis=1)
    table_data[empty_header(3)] = table_data.apply(lambda row: display_image(row, ""), axis=1)
    table_data['All time'] = table_data.apply(lambda row: display_artist(row, ""), axis=1)

    table_data.sort_values(by="Place", ascending=True, inplace=True)

    return table_data[['Place', empty_header(1), 'Last month', empty_header(2), 'Last 6 months', empty_header(3), 'All time']]


def display_image(row: pd.Series, suffix: str):
    if pd.isna(row["artist_image_url" + suffix]):
        return ''
    
    return md_image(row["artist_name" + suffix], row["artist_image_url" + suffix], 50)


def display_artist(row: pd.Series, suffix: str):
    return get_artist_link(row, output_dir(), suffix)
