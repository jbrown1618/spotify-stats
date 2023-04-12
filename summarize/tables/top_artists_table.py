import pandas as pd

from utils.markdown import md_image

def top_artists_table(top_artists: pd.DataFrame, artists: pd.DataFrame):
    top_artists_with_data = pd.merge(top_artists, artists, on="artist_uri")
    short = top_artists_with_data[top_artists_with_data['term'] == 'short_term']
    medium = top_artists_with_data[top_artists_with_data['term'] == 'medium_term']
    long = top_artists_with_data[top_artists_with_data['term'] == 'long_term']
    table_data = pd.merge(short, medium, on="index")
    table_data = pd.merge(table_data, long, on="index")

    table_data["Place"] = table_data["index"]
    table_data['Last month'] = table_data.apply(lambda row: display_artist(row, "_x"), axis=1)
    table_data['Last 6 months'] = table_data.apply(lambda row: display_artist(row, "_y"), axis=1)
    table_data['All time'] = table_data.apply(lambda row: display_artist(row, ""), axis=1)

    table_data.sort_values(by="Place", ascending=True, inplace=True)

    return table_data[['Place', 'Last month', 'Last 6 months', 'All time']]


def display_artist(row: pd.Series, suffix: str):
    return f'<div>{md_image(row["artist_name" + suffix], row["artist_image_url" + suffix], 50)} <span>{row["artist_name" + suffix]}</span></div>'