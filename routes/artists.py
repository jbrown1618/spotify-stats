import pandas as pd
import sqlalchemy

from data.database import get_engine
from data.filters import filtered_connection
from data.query import query_text
from routes.pagination import ARTIST_SORT_COLUMNS, paginate_df
from routes.utils import to_json


def artists_payload(filters: dict):
    with filtered_connection(filters) as (conn, params):
        artists = pd.read_sql_query(
            sqlalchemy.text(query_text('select_artists')),
            conn,
            params={
                "filter_artists": False,
                "artist_uris": ('EMPTY',),
                "filter_mbids": False,
                "mbids": ('EMPTY',),
                "wrapped_start_date": params["wrapped_start_date"],
                "wrapped_end_date": params["wrapped_end_date"],
            }
        )
    if artists.empty:
        return {"items": [], "total": 0}

    return paginate_df(artists, filters, ARTIST_SORT_COLUMNS, "Most streams")


RELATIONSHIP_COLUMNS = [
    "artist_mbid",
    "artist_mb_name",
    "artist_sort_name",
    "relationship_type",
    "relationship_direction",
    "artist_uri",
    "artist_name",
    "artist_image_url",
]


def artist_credits_payload(artist_uri: str):
    with get_engine().begin() as conn:
        credits = pd.read_sql_query(
            sqlalchemy.text(query_text("select_artist_credits")),
            conn,
            params={"artist_uri": artist_uri},
        )
        relationships = pd.read_sql_query(
            sqlalchemy.text(query_text("select_artist_relationships")),
            conn,
            params={"artist_uri": artist_uri},
        )

    result = {}
    if not credits.empty:
        result["credits"] = to_json(credits)

    aliases = _related_artists(
        relationships,
        relationship_types={"is person", "artist rename"},
    )
    if not aliases.empty:
        result["aliases"] = to_json(aliases[RELATIONSHIP_COLUMNS])

    members = _related_artists(
        relationships,
        relationship_types={"member of band"},
        direction="backward",
    )
    if not members.empty:
        result["members"] = to_json(members[RELATIONSHIP_COLUMNS])

    groups = _related_artists(
        relationships,
        relationship_types={"member of band"},
        direction="forward",
    )
    if not groups.empty:
        result["groups"] = to_json(groups[RELATIONSHIP_COLUMNS])

    subgroups = _related_artists(
        relationships,
        relationship_types={"subgroup"},
        direction="backward",
    )
    if not subgroups.empty:
        result["subgroups"] = to_json(subgroups[RELATIONSHIP_COLUMNS])

    return result


def _related_artists(
    relationships: pd.DataFrame,
    relationship_types: set[str],
    direction: str | None = None,
) -> pd.DataFrame:
    related = relationships[
        relationships["relationship_type"].isin(relationship_types)
    ]
    if direction is not None:
        related = related[related["relationship_direction"] == direction]
    return related.drop_duplicates(subset=["artist_mbid"], keep="first")