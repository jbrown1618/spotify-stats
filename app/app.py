import pandas as pd
from flask import Flask, request, send_file

from routes.albums import albums_payload
from routes.artists import artists_payload
from routes.filters import filter_options_payload
from routes.genres import genres_payload
from routes.labels import labels_payload
from routes.playlists import playlists_payload
from routes.release_years import release_years_payload
from routes.tracks import track_payload, tracks_search_payload
from routes.utils import to_date_range, to_json
from routes.producers import producers_payload
from data.sql.migrations.migrations import perform_all_migrations
from utils.ranking import album_ranks_over_time, album_streams_by_month, artist_ranks_over_time, artist_streams_by_month, track_ranks_over_time, track_streams_by_month

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


@app.route("/api/tracks/search", methods = ['POST'])
def search_tracks():
    return tracks_search_payload(request.json)


@app.route("/api/tracks/<track_uri>")
def get_track(track_uri):
    return track_payload(track_uri)


@app.route("/api/playlists", methods = ['POST'])
def list_playlists():
    return playlists_payload(request.json.get('tracks', None))


@app.route("/api/artists", methods = ['POST'])
def list_artists():
    return artists_payload(request.json.get('tracks', None))


@app.route("/api/albums", methods = ['POST'])
def list_albums():
    return albums_payload(request.json.get('tracks', None))


@app.route("/api/labels", methods = ['POST'])
def list_labels():
    return labels_payload(request.json.get('tracks', None))


@app.route("/api/genres", methods = ['POST'])
def list_genres():
    return genres_payload(request.json.get('tracks', None))


@app.route("/api/producers", methods=['POST'])
def list_producers():
    return producers_payload(request.json.get('tracks', None))


@app.route("/api/release-years", methods = ['POST'])
def list_release_years():
    return release_years_payload(request.json.get('tracks', None))


@app.route("/api/streams/tracks/history", methods = ['POST'])
def list_track_stream_history():
    track_uris = request.json.get('tracks', None)
    if track_uris is None or len(track_uris) == 0:
        return []
    min_date, max_date = to_date_range(request.json.get('wrapped', None))
    return to_json(track_ranks_over_time(track_uris, min_date, max_date))


@app.route("/api/streams/tracks/months", methods = ['POST'])
def list_track_streams_by_month():
    track_uris = request.json.get('tracks', None)
    if track_uris is None or len(track_uris) == 0:
        return {}
    min_date, max_date = to_date_range(request.json.get('wrapped', None))
    return track_streams_by_month(track_uris, min_date, max_date)


@app.route("/api/streams/artists/history", methods = ['POST'])
def list_artist_stream_history():
    artist_uris = request.json.get('artists', None)
    if artist_uris is None or len(artist_uris) == 0:
        return []
    min_date, max_date = to_date_range(request.json.get('wrapped', None))
    return to_json(artist_ranks_over_time(artist_uris, min_date, max_date))


@app.route("/api/streams/artists/months", methods = ['POST'])
def list_artist_streams_by_month():
    artist_uris = request.json.get('artists', None)
    if artist_uris is None or len(artist_uris) == 0:
        return {}
    min_date, max_date = to_date_range(request.json.get('wrapped', None))
    return artist_streams_by_month(artist_uris, min_date, max_date)


@app.route("/api/streams/albums/history", methods = ['POST'])
def list_album_stream_history():
    album_uris = request.json.get('albums', None)
    if album_uris is None or len(album_uris) == 0:
        return []
    min_date, max_date = to_date_range(request.json.get('wrapped', None))
    return to_json(album_ranks_over_time(album_uris, min_date, max_date))


@app.route("/api/streams/albums/months", methods = ['POST'])
def list_album_streams_by_month():
    album_uris = request.json.get('albums', None)
    if album_uris is None or len(album_uris) == 0:
        return {}
    min_date, max_date = to_date_range(request.json.get('wrapped', None))
    return album_streams_by_month(album_uris, min_date, max_date)
