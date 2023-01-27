import re
import pandas as pd


more_than_three_hyphens = re.compile(r"-{3,}")
more_than_one_space = re.compile(r" {1,}")

def md_link(text: str, url: str):
    return f"[{text}]({url})"


def md_summary_details(summary: str, details: str):
    return f"""
<details>
<summary>{summary}</summary>

{details}

</details>
"""


def md_image(alt_text: str, url: str, width=None):
    if width is None:
        return f"![{alt_text}]({url})"

    return f'<img src="{url}" alt="{alt_text}" width="{width}" />'


def md_table(df: pd.DataFrame):
    table = df.to_markdown(index=False)
    table = more_than_one_space.sub(' ', table) # Consolidate spaces into two
    table = more_than_three_hyphens.sub('---', table) # Consolidate dashes into three
    return table