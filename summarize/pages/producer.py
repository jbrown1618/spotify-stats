from data.provider import DataProvider
from utils.path import producer_overview_path


def make_producer_summary(mbid: str):
    dp = DataProvider()
    mb_artist = dp.mb_artist(mbid=mbid)

    name = None
    if mb_artist['artist_mb_name'].isascii():
        name = mb_artist['artist_mb_name']
    else:
        name = f"{mb_artist['artist_mb_name']} ({mb_artist['artist_sort_name']})"

    print(f"Generating summary for producer {name}")

    content = []
    content += title(name)

    with open(producer_overview_path(name), "w") as f:
        f.write("\n".join(content))


def title(producer_name):
    return [f"# {producer_name}", ""]