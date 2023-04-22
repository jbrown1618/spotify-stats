import pandas as pd

from utils.markdown import md_image

def top_tracks_table(top_tracks: pd.DataFrame, tracks: pd.DataFrame):
    top_tracks_with_data = pd.merge(top_tracks, tracks, on="track_uri")
    short = top_tracks_with_data[top_tracks_with_data['term'] == 'short_term']
    medium = top_tracks_with_data[top_tracks_with_data['term'] == 'medium_term']
    long = top_tracks_with_data[top_tracks_with_data['term'] == 'long_term']
    table_data = pd.merge(short, medium, on="index", how="outer")
    table_data = pd.merge(table_data, long, on="index", how="outer")

    table_data["Place"] = table_data["index"]
    table_data['Last month'] = table_data.apply(lambda row: display_track(row, "_x"), axis=1)
    table_data['Last 6 months'] = table_data.apply(lambda row: display_track(row, "_y"), axis=1)
    table_data['All time'] = table_data.apply(lambda row: display_track(row, ""), axis=1)

    table_data.sort_values(by="Place", ascending=True, inplace=True)

    return table_data[['Place', 'Last month', 'Last 6 months', 'All time']]


def display_track(row: pd.Series, suffix: str):
    if pd.isna(row["track_name" + suffix]):
        return ''
    
    return f'<div>{md_image(row["album_name" + suffix], row["album_image_url" + suffix], 50)} <span>{row["track_name" + suffix]}</span></div>'