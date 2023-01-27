import pandas as pd

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
    return df.to_markdown(index=False)