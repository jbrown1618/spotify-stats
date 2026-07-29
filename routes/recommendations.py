import json

import pandas as pd
import sqlalchemy

from data.filters import filtered_connection, parse_filters
from data.query import query_text


def _has_active_filters(params: dict) -> bool:
    return any([
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


def percentile_range_recommendations_payload(filters: dict, low_percentile: float, high_percentile: float):
    """Return tracks matching the current filter whose stream totals fall within
    [low_percentile, high_percentile] (each 0.0 to 1.0), sorted least-recently-streamed first.

    Always returns a dict with 'items' (a page of full track records) and 'total'.
    If 'limit' is present in filters, slices to the requested page; otherwise returns all items.
    """
    if low_percentile > high_percentile:
        low_percentile, high_percentile = high_percentile, low_percentile

    params = parse_filters(filters)
    has_filters = _has_active_filters(params)

    with filtered_connection(filters) as (conn, filter_params):
        if has_filters:
            # Check track count to avoid showing recommendations for very small filter sets
            track_count = pd.read_sql_query(
                sqlalchemy.text("SELECT COUNT(*) AS cnt FROM matching_track_uris"),
                conn
            ).iloc[0]['cnt']
            if track_count < 60:
                return {"items": [], "total": 0}

        track_recs = pd.read_sql_query(
            sqlalchemy.text(query_text('select_track_recommendations_percentile_range')),
            conn,
            params={
                'low_percentile': low_percentile,
                'high_percentile': high_percentile,
                'filter_tracks': has_filters,
            }
        )

    total = len(track_recs)

    limit = filters.get('limit')
    if limit is not None:
        offset = filters.get('offset', 0)
        track_recs = track_recs.iloc[offset:offset + limit]

    items = json.loads(track_recs.fillna(value=pd.NA).to_json(orient="records"))
    return {"items": items, "total": total}
