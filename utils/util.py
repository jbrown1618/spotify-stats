import re
import pandas as pd


def get_id(uri: str):
    last_colon = uri.rindex(":") + 1
    return uri[last_colon:]


def md_link(text: str, url: str):
    return f"[{text}]({url})"


def md_summary_details(summary: str, details: str):
    return f"""
<details>
<summary>{summary}</summary>

{details}

</details>
"""


def md_image(alt_text: str, url: str):
    return f"![{alt_text}]({url})"


def file_name_friendly(text: str):
    return re.sub(r"[^a-z0-9]", "_", text.lower())


def prefix_df(df: pd.DataFrame, prefix: str, prefixes: list[str]):
    df.columns = [prefix_col(col, prefix, prefixes) for col in df.columns]


def prefix_col(col: str, prefix: str, prefixes: list[str]):
    for other_prefix in prefixes:
        if col.startswith(other_prefix):
            return col
    return prefix + col