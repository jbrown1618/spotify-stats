import pandas as pd
import sqlalchemy

from data.query import query_text
from data.raw import get_engine


def recommendations_payload():
    recommendations = {}

    with get_engine().begin() as conn:
        track_recs = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_recommendations_jump_back_in')),
            conn,
            params={'percentile': 0.6}
        )
        if not track_recs.empty:
            recommendations["It's been a long time"] = {
                "type": "track",
                "uris": track_recs['track_uri'].tolist()
            }

        top_tracks = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_recommendations_jump_back_in')),
            conn,
            params={'percentile': 0.9}
        )
        if not top_tracks.empty:
            recommendations["Jump back in"] = {
                "type": "track",
                "uris": top_tracks['track_uri'].tolist()
            }

        artist_recs = pd.read_sql_query(
            sqlalchemy.text(query_text('select_artist_recommendations_rediscover')),
            conn,
            params={'percentile': 0.95}
        )
        if not artist_recs.empty:
            recommendations["Rediscover artists"] = {
                "type": "artist",
                "uris": artist_recs['artist_uri'].tolist()
            }

    return recommendations
