import pandas as pd
from data.provider import DataProvider
from summarize.tables.artists_table import artists_table
from summarize.tables.producers_table import co_producers_table, production_credits_table
from utils.artist_relationship import mb_artist_name
from utils.markdown import md_table, md_truncated_table
from utils.path import producer_overview_path, producer_path


def make_producer_summary(mbid: str):
    dp = DataProvider()
    mb_artist = dp.mb_artist(mbid=mbid)

    name = mb_artist_name(mb_artist['artist_mb_name'], mb_artist['artist_sort_name'])

    print(f"Generating summary for producer {name}")

    credits = DataProvider().track_credits(artist_mbids={mbid}, include_aliases=True)

    content = []
    content += title(name)
    content += credit_types_section(mbid, credits)
    content += produces_for_artists_section(name, credits)
    content += works_with_section(mbid, name)
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
    table = artists_table(DataProvider().tracks(track_uris), producer_path(name))
    return [
        '## Produces for Artists',
        '',
        md_truncated_table(table),
        ''
    ]


def works_with_section(mbid, name):
    table = co_producers_table(mbid, producer_path(name))
    if table is None:
        return []
    
    return [
        '## Works with Producers',
        '',
        md_truncated_table(table),
        ''
    ]


def production_credits_section(mbid: str, name: str):
    table = production_credits_table(artist_mbid=mbid, relative_to=producer_overview_path(name))
    return [
        "## Production Credits",
        "",
        md_table(table)
    ]