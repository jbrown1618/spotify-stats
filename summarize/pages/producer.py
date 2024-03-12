import pandas as pd
from data.provider import DataProvider
from summarize.tables.artists_table import artists_table
from summarize.tables.production_credits_table import production_credits_table
from utils.markdown import md_image, md_table
from utils.path import producer_overview_path
from utils.util import first


def make_producer_summary(mbid: str):
    dp = DataProvider()
    mb_artist = dp.mb_artist(mbid=mbid)

    name = None
    if mb_artist['artist_mb_name'].isascii():
        name = mb_artist['artist_mb_name']
    else:
        name = f"{mb_artist['artist_mb_name']} ({mb_artist['artist_sort_name']})"

    print(f"Generating summary for producer {name}")

    credits = DataProvider().track_credits(artist_mbids={mbid}, include_aliases=True)

    content = []
    content += title(name)
    content += credit_types_section(mbid, credits)
    content += produces_for_artists_section(name, credits)
    content += works_with_section()
    content += production_credits_section(mbid, name)

    with open(producer_overview_path(name), "w") as f:
        f.write("\n".join(content))


def title(producer_name):
    return [f"# {producer_name} (Producer)", ""]


def credit_types_section(mbid, credits):
    credits = DataProvider().track_credits(artist_mbids={mbid}, include_aliases=True)
    if len(credits) == 0:
        return []

    credits_by_type = credits.groupby("credit_type").agg({"recording_mbid": "count"}).reset_index()
    credits_by_type['credit_type'] = credits_by_type['credit_type'].apply(lambda t: t.capitalize())
    credits_by_type = credits_by_type.rename(columns={"credit_type": "Credit Type", "recording_mbid": "Tracks"})
    return [
        '## Credits by Type',
        '',
        md_table(credits_by_type),
        ''
    ]


def produces_for_artists_section(name, credits: pd.DataFrame):
    track_uris = credits['track_uri']
    table = artists_table(DataProvider().tracks(track_uris), producer_overview_path(name))

    return [
        '## Produces for Artists',
        '',
        md_table(table),
        ''
    ]


def works_with_section():
    return [
        '## Works with Producers',
        ''
    ]


def production_credits_section(mbid: str, name: str):
    table = production_credits_table(artist_mbid=mbid, relative_to=producer_overview_path(name))
    return [
        "## Production Credits",
        "",
        md_table(table)
    ]