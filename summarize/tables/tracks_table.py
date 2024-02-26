import pandas as pd

from utils.artist import get_display_artists
from utils.markdown import md_image
from utils.record_label import get_display_labels
from utils.util import spotify_link

artist_sorting = ["artist_names_sorting", "negative_track_score", "album_release_date", "Album", "Track"]
default_sorting = ["negative_track_score", "album_release_date", "Album", "Track"]
chronological_sorting = ["album_release_date", "Album", "Track"]
no_sorting = []

def tracks_table(tracks: pd.DataFrame, relative_to: str, sorting: str = None):
    table_data = tracks.copy()
    table_data['negative_track_score'] = table_data['track_score'] * -1
    table_data["artist_names_sorting"] = table_data["primary_artist_name"]
    table_data["Art"] = table_data["album_image_url"].apply(lambda src: md_image("", src, 50))
    table_data["Artists"] = table_data["track_uri"].apply(lambda track_uri: get_display_artists(track_uri, relative_to))
    table_data["Track"] = table_data["track_name"]
    table_data["🔗"] = table_data["track_uri"].apply(lambda uri: spotify_link(uri))
    table_data["Album"] = table_data["album_name"]
    table_data["Label"] = table_data["album_label"].apply(lambda label: get_display_labels(label, relative_to))
    table_data["Score"] = table_data["track_score"]
    table_data["💚"] = table_data["track_liked"].apply(lambda liked: "💚" if liked else "")

    if sorting is not None:
        sort_cols = artist_sorting if sorting == 'artist' \
            else chronological_sorting if sorting == 'chronological' \
            else default_sorting 

        table_data = table_data.sort_values(by=sort_cols)
    
    return table_data[["Art", "Track", "Album", "Artists", "Label", "Score", "💚", "🔗"]]
