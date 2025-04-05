import pandas as pd
from flask import Flask, request, send_file

from app.routes.albums import albums_payload
from app.routes.artists import artists_payload
from app.routes.genres import genres_payload
from app.routes.labels import labels_payload
from app.routes.playlists import playlists_payload
from app.routes.release_years import release_years_payload
from app.routes.summary import summary_payload
from app.routes.tracks import track_payload, tracks_search_payload
from app.utils import to_filters, to_track_uris
from data.sql.migrations.migrations import perform_all_migrations

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


@app.route("/api/release_years")
def list_release_years():
    return release_years_payload(to_track_uris(request.args))
