from flask import Flask

from data.provider import DataProvider

app = Flask(__name__)


@app.route("/tracks")
def data():
    tracks = DataProvider().tracks().head(10)
    return tracks.to_html()


@app.route("/artists")
def dataa():
    tracks = DataProvider().artists().head(10)
    return tracks.to_html()