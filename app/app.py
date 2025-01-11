import pandas as pd
from flask import Flask, send_file

from api.summary import summary_payload
from api.wrapped import wrapped_payload
from data.sql.migrations.migrations import perform_all_migrations

pd.options.mode.chained_assignment = None  # default='warn'
app = Flask(__name__)


with app.app_context():
    perform_all_migrations()


@app.route("/")
def index():
    return send_file("./static/index.html")


@app.route("/api/summary")
def summary():
    return summary_payload()


@app.route("/api/wrapped/<year>")
def wrapped(year):
    return wrapped_payload(int(year))
