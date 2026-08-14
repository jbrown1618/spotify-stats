import json

import pandas as pd

from data.repository import DataRepository


repository = DataRepository()


def percentile_range_recommendations_payload(filters: dict, low_percentile: float, high_percentile: float):
    """Return tracks matching the current filter whose stream totals fall within
    [low_percentile, high_percentile] (each 0.0 to 1.0), sorted least-recently-streamed first.

    Always returns a dict with 'items' (a page of full track records) and 'total'.
    If 'limit' is present in filters, slices to the requested page; otherwise returns all items.
    """
    if low_percentile > high_percentile:
        low_percentile, high_percentile = high_percentile, low_percentile

    recommendations = repository.track_recommendations(
        filters,
        low_percentile,
        high_percentile,
        minimum_track_count=60,
    )
    if recommendations.tracks is None:
        return {"items": [], "total": 0}

    track_recs = recommendations.tracks

    total = len(track_recs)

    limit = filters.get('limit')
    if limit is not None:
        offset = filters.get('offset', 0)
        track_recs = track_recs.iloc[offset:offset + limit]

    items = json.loads(track_recs.fillna(value=pd.NA).to_json(orient="records"))
    return {"items": items, "total": total}
