import pandas as pd
import sqlalchemy

from data.query import query_text
from data.raw import get_engine


# Percentile thresholds for recommendations
TRACK_PERCENTILE = 0.75  # Top 25% most-listened liked tracks
ARTIST_PERCENTILE = 0.80  # Top 20% most-listened artists


def recommendations_payload():
    """
    Returns recommendation lists in the format:
    {
        "Jump back in": {"type": "track", "uris": [...track uris...]},
        "Rediscover artists": {"type": "artist", "uris": [...artist uris...]}
    }
    """
    recommendations = {}

    with get_engine().begin() as conn:
        # Get track recommendations - liked tracks with significant history not played recently
        track_recs = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_recommendations_jump_back_in')),
            conn,
            params={'percentile': TRACK_PERCENTILE}
        )
        if not track_recs.empty:
            recommendations["Jump back in"] = {
                "type": "track",
                "uris": track_recs['track_uri'].tolist()
            }

        # Get artist recommendations - artists with significant history not played recently
        artist_recs = pd.read_sql_query(
            sqlalchemy.text(query_text('select_artist_recommendations_rediscover')),
            conn,
            params={'percentile': ARTIST_PERCENTILE}
        )
        if not artist_recs.empty:
            recommendations["Rediscover artists"] = {
                "type": "artist",
                "uris": artist_recs['artist_uri'].tolist()
            }

    return recommendations
