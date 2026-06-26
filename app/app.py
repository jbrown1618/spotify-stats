import pandas as pd
from flask import Flask, request, send_file

from routes.albums import albums_payload
from routes.artists import artists_payload, artist_credits_payload
from routes.filters import filter_options_payload
from routes.genres import genres_payload
from routes.insights import insights_payload
from routes.labels import labels_payload
from routes.playlists import playlists_payload
from routes.recommendations import recommendations_payload
from routes.release_years import release_years_payload
from routes.stream_shares import artist_stream_share_by_month_payload, genre_stream_share_by_month_payload
from routes.tracks import tracks_search_payload, track_credits_payload
from routes.utils import to_date_range, to_json
from routes.producers import producers_payload
from data.filters import parse_request_args
from data.sql.migrations.migrations import perform_all_migrations
from spotify.spotify_client import spotify_auth_status
from utils.ranking import album_ranks_over_time, album_streams_by_month, artist_ranks_over_time, artist_streams_by_month, track_ranks_over_time, track_streams_by_month
from utils.ranking import filtered_track_ranks_over_time, filtered_track_streams_by_month, filtered_artist_ranks_over_time, filtered_artist_streams_by_month, filtered_album_ranks_over_time, filtered_album_streams_by_month

pd.options.mode.chained_assignment = None  # default='warn'
app = Flask(__name__)

with app.app_context():
    perform_all_migrations()


@app.route("/")
def index():
    return send_file("./static/index.html")


@app.route("/api/filters")
def get_filter_options():
    return filter_options_payload()


@app.route("/api/spotify-auth/status")
def get_spotify_auth_status():
    return spotify_auth_status()


@app.route("/api/tracks")
def list_tracks():
    return tracks_search_payload(parse_request_args(request.args))


@app.route("/api/tracks/<track_uri>/credits")
def get_track_credits(track_uri):
    return track_credits_payload(track_uri)


@app.route("/api/playlists")
def list_playlists():
    return playlists_payload(parse_request_args(request.args))


@app.route("/api/artists")
def list_artists():
    return artists_payload(parse_request_args(request.args))


@app.route("/api/artists/<artist_uri>/credits")
def get_artist_credits(artist_uri):
    return artist_credits_payload(artist_uri)


@app.route("/api/albums")
def list_albums():
    return albums_payload(parse_request_args(request.args))


@app.route("/api/labels")
def list_labels():
    return labels_payload(parse_request_args(request.args))


@app.route("/api/genres")
def list_genres():
    return genres_payload(parse_request_args(request.args))


@app.route("/api/producers")
def list_producers():
    return producers_payload(parse_request_args(request.args))


@app.route("/api/release-years")
def list_release_years():
    return release_years_payload(parse_request_args(request.args))


@app.route("/api/insights")
def get_insights():
    return insights_payload(parse_request_args(request.args))


@app.route("/api/streams/tracks/history")
def list_track_stream_history():
    params = parse_request_args(request.args)
    n = params.get('n', 10)
    track_uris = params.get('tracks', None)
    if track_uris is not None:
        if len(track_uris) == 0:
            return []
        min_date, max_date = to_date_range(params.get('wrapped', None))
        return to_json(track_ranks_over_time(track_uris, min_date, max_date))
    return to_json(filtered_track_ranks_over_time(params, n))


@app.route("/api/streams/tracks/months")
def list_track_streams_by_month():
    params = parse_request_args(request.args)
    n = params.get('n', 5)
    track_uris = params.get('tracks', None)
    if track_uris is not None:
        if len(track_uris) == 0:
            return {"streams": {}, "metadata": {}}
        min_date, max_date = to_date_range(params.get('wrapped', None))
        return track_streams_by_month(track_uris, min_date, max_date)
    return filtered_track_streams_by_month(params, n)


@app.route("/api/streams/artists/history")
def list_artist_stream_history():
    params = parse_request_args(request.args)
    n = params.get('n', 10)
    artist_uris = params.get('artists', None)
    if artist_uris is not None:
        if len(artist_uris) == 0:
            return []
        min_date, max_date = to_date_range(params.get('wrapped', None))
        return to_json(artist_ranks_over_time(artist_uris, min_date, max_date))
    return to_json(filtered_artist_ranks_over_time(params, n))


@app.route("/api/streams/artists/months")
def list_artist_streams_by_month():
    params = parse_request_args(request.args)
    n = params.get('n', 5)
    artist_uris = params.get('artists', None)
    if artist_uris is not None:
        if len(artist_uris) == 0:
            return {"streams": {}, "metadata": {}}
        min_date, max_date = to_date_range(params.get('wrapped', None))
        return artist_streams_by_month(artist_uris, min_date, max_date)
    return filtered_artist_streams_by_month(params, n)


@app.route("/api/streams/artists/share")
def list_artist_stream_share_by_month():
    return artist_stream_share_by_month_payload(parse_request_args(request.args))


@app.route("/api/streams/albums/history")
def list_album_stream_history():
    params = parse_request_args(request.args)
    n = params.get('n', 10)
    album_uris = params.get('albums', None)
    if album_uris is not None:
        if len(album_uris) == 0:
            return []
        min_date, max_date = to_date_range(params.get('wrapped', None))
        return to_json(album_ranks_over_time(album_uris, min_date, max_date))
    return to_json(filtered_album_ranks_over_time(params, n))


@app.route("/api/streams/albums/months")
def list_album_streams_by_month():
    params = parse_request_args(request.args)
    n = params.get('n', 5)
    album_uris = params.get('albums', None)
    if album_uris is not None:
        if len(album_uris) == 0:
            return {"streams": {}, "metadata": {}}
        min_date, max_date = to_date_range(params.get('wrapped', None))
        return album_streams_by_month(album_uris, min_date, max_date)
    return filtered_album_streams_by_month(params, n)


@app.route("/api/streams/genres/share")
def list_genre_stream_share_by_month():
    return genre_stream_share_by_month_payload(parse_request_args(request.args))


@app.route("/api/recommendations")
def get_recommendations():
    return recommendations_payload(parse_request_args(request.args))
