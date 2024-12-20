import pandas as pd

from data.provider import DataProvider
from utils.markdown import empty_header, md_image, md_link, md_table
from utils.path import artist_overview_path
from utils.top_lists import get_term_length_description

def top_tracks_table(tracks: pd.DataFrame, relative_to):
    top_tracks = DataProvider().top_tracks(current=True)

    top_tracks_with_data = pd.merge(top_tracks, tracks, on="track_uri")
    short = top_tracks_with_data[top_tracks_with_data['term'] == 'short_term']
    medium = top_tracks_with_data[top_tracks_with_data['term'] == 'medium_term']
    long = top_tracks_with_data[top_tracks_with_data['term'] == 'long_term']

    table_data = pd.merge(short, medium, on="index", how="outer")
    table_data = pd.merge(table_data, long, on="index", how="outer")

    table_data["Place"] = table_data["index"]
    table_data[empty_header(1)] = table_data.apply(lambda row: display_image(row, "_x"), axis=1)
    table_data[get_term_length_description('short_term')] = table_data.apply(lambda row: display_track(row, "_x", relative_to), axis=1)
    table_data[empty_header(2)] = table_data.apply(lambda row: display_image(row, "_y"), axis=1)
    table_data[get_term_length_description('medium_term')] = table_data.apply(lambda row: display_track(row, "_y", relative_to), axis=1)
    table_data[empty_header(3)] = table_data.apply(lambda row: display_image(row, ""), axis=1)
    table_data[get_term_length_description('long_term')] = table_data.apply(lambda row: display_track(row, "", relative_to), axis=1)

    table_data.sort_values(by="Place", ascending=True, inplace=True)

    return table_data[[
        'Place', 
        empty_header(1), get_term_length_description('short_term'), 
        empty_header(2), get_term_length_description('medium_term'), 
        empty_header(3), get_term_length_description('long_term')
    ]]


def display_image(row: pd.Series, suffix: str):
    if pd.isna(row["album_image_url" + suffix]):
        return ''
    
    return md_image(row["album_name" + suffix], row["album_image_url" + suffix], 50)


def display_track(row: pd.Series, suffix: str, relative_to: str):
    if pd.isna(row["track_name" + suffix]):
        return ''
    
    text = row["track_name" + suffix]

    uri = artist_overview_path(row["primary_artist_name" + suffix], relative_to) if row["primary_artist_has_page" + suffix] else None

    return md_link(text, uri) if uri is not None else text


def most_and_least_listened_tracks_table(tracks: pd.DataFrame, relative_to: str):
    top_count = min(10, tracks.size / 2)

    top_tracks = tracks.sort_values(by=["track_rank", 'track_uri'], ascending=True)\
        .head(top_count)\
        .reset_index()
    
    bottom_tracks = tracks.sort_values(by=["track_rank", 'track_uri'], ascending=False)\
        .head(top_count)\
        .reset_index()

    data = pd.DataFrame({
        "Rank": top_tracks["track_rank"],
        empty_header(1): top_tracks.apply(lambda row: display_image(row, ""), axis=1),
        "Most listened tracks": top_tracks.apply(lambda row: display_track(row, "", relative_to), axis=1),
        "Rank ": bottom_tracks["track_rank"],
        empty_header(2): bottom_tracks.apply(lambda row: display_image(row, ""), axis=1),
        "Least listened tracks": bottom_tracks.apply(lambda row: display_track(row, "", relative_to), axis=1)
    })
    
    return md_table(data)