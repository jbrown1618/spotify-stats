import pandas as pd
from flask import Flask, request, send_file

from routes.albums import albums_payload
from routes.artists import artists_payload
from routes.filters import filter_options_payload
from routes.genres import genres_payload
from routes.labels import labels_payload
from routes.playlists import playlists_payload
from routes.release_years import release_years_payload
from routes.summary import summary_payload
from routes.tracks import track_payload, tracks_search_payload
from routes.utils import to_album_uris, to_artist_uris, to_date_range, to_filters, to_json, to_track_uris
from data.sql.migrations.migrations import perform_all_migrations
from utils.ranking import album_ranks_over_time, album_streams_by_month, artist_ranks_over_time, artist_streams_by_month, track_ranks_over_time, track_streams_by_month

pd.options.mode.chained_assignment = None  # default='warn'
app = Flask(__name__)


with app.app_context():
    perform_all_migrations()


@app.route("/")
def index():
    return send_file("./static/index.html")


@app.route("/api/summary")
def get_summary():
    return summary_payload()


@app.route("/api/filters")
def get_filter_options():
    return filter_options_payload()


@app.route("/api/tracks/search")
def search_tracks():
    return tracks_search_payload(to_filters(request.args))


@app.route("/api/tracks/<track_uri>")
def get_track(track_uri):
    return track_payload(track_uri)


@app.route("/api/playlists")
def list_playlists():
    return playlists_payload(to_track_uris(request.args))


@app.route("/api/artists")
def list_artists():
    return artists_payload(to_track_uris(request.args))


@app.route("/api/albums")
def list_albums():
    return albums_payload(to_track_uris(request.args))


@app.route("/api/labels")
def list_labels():
    return labels_payload(to_track_uris(request.args))


@app.route("/api/genres")
def list_genres():
    return genres_payload(to_track_uris(request.args))


@app.route("/api/release-years")
def list_release_years():
    return release_years_payload(to_track_uris(request.args))


@app.route("/api/streams/tracks/history")
def list_track_stream_history():
    min_date, max_date = to_date_range(request.args)
    return to_json(track_ranks_over_time(to_track_uris(request.args), min_date, max_date))


@app.route("/api/streams/tracks/months")
def list_track_streams_by_month():
    min_date, max_date = to_date_range(request.args)
    return track_streams_by_month(to_track_uris(request.args), min_date, max_date)


@app.route("/api/streams/artists/history")
def list_artist_stream_history():
    min_date, max_date = to_date_range(request.args)
    return to_json(artist_ranks_over_time(to_artist_uris(request.args), min_date, max_date))


@app.route("/api/streams/artists/months")
def list_artist_streams_by_month():
    min_date, max_date = to_date_range(request.args)
    return artist_streams_by_month(to_artist_uris(request.args), min_date, max_date)


@app.route("/api/streams/albums/history")
def list_album_stream_history():
    min_date, max_date = to_date_range(request.args)
    return to_json(album_ranks_over_time(to_album_uris(request.args), min_date, max_date))


@app.route("/api/streams/albums/months")
def list_album_streams_by_month():
    min_date, max_date = to_date_range(request.args)
    return album_streams_by_month(to_album_uris(request.args), min_date, max_date)
