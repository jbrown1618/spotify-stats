import pandas as pd
import sqlalchemy

from data.filters import filtered_connection, parse_filters
from data.query import query_text


def recommendations_payload(filters: dict):
    recommendations = {}
    
    params = parse_filters(filters)
    
    # Determine if any filters are active
    has_filters = any([
        params["filter_tracks"],
        params["filter_playlists"],
        params["filter_artists"],
        params["filter_albums"],
        params["filter_labels"],
        params["filter_genres"],
        params["filter_producers"],
        params["filter_years"],
        params["liked"],
        params["wrapped_start_date"] is not None,
    ])

    with filtered_connection(filters) as (conn, filter_params):
        if has_filters:
            # Check track count to avoid showing recommendations for very small filter sets
            track_count = pd.read_sql_query(
                sqlalchemy.text("SELECT COUNT(*) AS cnt FROM matching_track_uris"),
                conn
            ).iloc[0]['cnt']
            if track_count < 60:
                return recommendations
        
        filter_tracks = has_filters

        still_interested_tracks = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_recommendations_still_interested')),
            conn,
            params={
                'percentile': 0.6,
                'filter_tracks': filter_tracks,
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
                'filter_by_date': True,
                'filter_tracks': filter_tracks,
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
                'filter_by_date': False,
                'filter_tracks': filter_tracks,
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
            }
        )
        if not album_recs.empty and len(album_recs) >= 5:
            recommendations["Rediscover albums"] = {
                "type": "album",
                "uris": album_recs['album_uri'].tolist()
            }

    return recommendations
