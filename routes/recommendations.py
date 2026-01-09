import typing
import pandas as pd
import sqlalchemy

from data.query import query_text
from data.raw import get_engine


def recommendations_payload(track_uris: typing.Optional[typing.List[str]] = None):
    recommendations = {}
    
    filter_tracks = track_uris is not None and len(track_uris) > 0
    
    # Don't show recommendations if viewing fewer than 60 tracks
    if filter_tracks and len(track_uris) < 60:
        return recommendations
    
    # Use a tuple for SQL IN clause, with a dummy value if empty to avoid SQL errors
    track_uris_tuple = tuple(track_uris) if filter_tracks else ('__none__',)

    with get_engine().begin() as conn:
        still_interested_tracks = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_recommendations_still_interested')),
            conn,
            params={
                'percentile': 0.6,
                'filter_tracks': filter_tracks,
                'track_uris': track_uris_tuple
            }
        )
        if not still_interested_tracks.empty and len(still_interested_tracks) >= 5:
            recommendations["Still interested?"] = {
                "type": "track",
                "uris": still_interested_tracks['track_uri'].tolist()
            }

        track_recs = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_recommendations_jump_back_in')),
            conn,
            params={
                'percentile': 0.6,
                'filter_tracks': filter_tracks,
                'track_uris': track_uris_tuple
            }
        )
        if not track_recs.empty and len(track_recs) >= 5:
            recommendations["It's been a long time"] = {
                "type": "track",
                "uris": track_recs['track_uri'].tolist()
            }

        top_tracks = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_recommendations_jump_back_in')),
            conn,
            params={
                'percentile': 0.9,
                'filter_tracks': filter_tracks,
                'track_uris': track_uris_tuple
            }
        )
        if not top_tracks.empty and len(top_tracks) >= 5:
            recommendations["Jump back in"] = {
                "type": "track",
                "uris": top_tracks['track_uri'].tolist()
            }

        artist_recs = pd.read_sql_query(
            sqlalchemy.text(query_text('select_artist_recommendations_rediscover')),
            conn,
            params={
                'percentile': 0.85,
                'filter_tracks': filter_tracks,
                'track_uris': track_uris_tuple
            }
        )
        if not artist_recs.empty and len(artist_recs) >= 5:
            recommendations["Rediscover artists"] = {
                "type": "artist",
                "uris": artist_recs['artist_uri'].tolist()
            }

        album_recs = pd.read_sql_query(
            sqlalchemy.text(query_text('select_album_recommendations_rediscover')),
            conn,
            params={
                'percentile': 0.8,
                'filter_tracks': filter_tracks,
                'track_uris': track_uris_tuple
            }
        )
        if not album_recs.empty and len(album_recs) >= 5:
            recommendations["Rediscover albums"] = {
                "type": "album",
                "uris": album_recs['album_uri'].tolist()
            }

    return recommendations
