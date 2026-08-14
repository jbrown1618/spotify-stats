import pandas as pd

from data.repository import DataRepository
from routes.pagination import ARTIST_SORT_COLUMNS, paginate_df
from routes.utils import to_json


repository = DataRepository()


def artists_payload(filters: dict):
    artists = repository.artists_for_filters(filters)
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
    artist_credits = repository.artist_credits(artist_uri)
    credits = artist_credits.credits
    relationships = artist_credits.relationships

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