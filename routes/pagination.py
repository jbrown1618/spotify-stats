import json

import pandas as pd


TRACK_SORT_COLUMNS = {
    "Most streams": ("track_stream_count", False),
    "Least streams": ("track_stream_count", True),
    "Recently played": ("track_last_played_at", False),
    "Least recently played": ("track_last_played_at", True),
    "Newest": ("album_release_date", False),
    "Oldest": ("album_release_date", True),
    "Alphabetical": ("track_name", True),
}

ARTIST_SORT_COLUMNS = {
    "Most streams": ("artist_stream_count", False),
    "Least streams": ("artist_stream_count", True),
    "Most liked tracks": ("artist_liked_track_count", False),
    "Alphabetical": ("artist_name", True),
}

ALBUM_SORT_COLUMNS = {
    "Most streams": ("album_stream_count", False),
    "Least streams": ("album_stream_count", True),
    "Most liked tracks": ("album_liked_track_count", False),
    "Newest": ("album_release_date", False),
    "Oldest": ("album_release_date", True),
    "Alphabetical": ("album_name", True),
}

PLAYLIST_SORT_COLUMNS = {
    "Most liked tracks": ("playlist_liked_track_count", False),
}

LABEL_SORT_COLUMNS = {
    "Most liked tracks": ("liked_track_count", False),
}

GENRE_SORT_COLUMNS = {
    "Most liked tracks": ("liked_track_count", False),
}

RELEASE_YEAR_SORT_COLUMNS = {
    "Newest": ("release_year", False),
    "Oldest": ("release_year", True),
    "Most liked tracks": ("liked_track_count", False),
}

PRODUCER_SORT_COLUMNS = {
    "Most tracks": ("track_count", False),
}


def paginate_df(df, filters, sort_columns, default_sort):
    """Sort and optionally paginate the DataFrame.
    
    Always returns a dict with 'items' and 'total'.
    If 'limit' is present in filters, slices to the requested page.
    Otherwise returns all items.
    """
    sort = filters.get('sort', default_sort)
    col, ascending = sort_columns.get(sort, sort_columns[default_sort])
    df = df.sort_values(col, ascending=ascending, na_position='last')

    total = len(df)

    limit = filters.get('limit')
    if limit is not None:
        offset = filters.get('offset', 0)
        df = df.iloc[offset:offset + limit]

    items = json.loads(df.fillna(value=pd.NA).to_json(orient="records"))
    return {"items": items, "total": total}
