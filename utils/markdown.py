import re
import html
import pandas as pd


more_than_three_hyphens = re.compile(r"-{3,}")
more_than_one_space = re.compile(r" {1,}")

def md_link(text: str, url: str):
    return f"[{text}]({url})"


def md_summary_details(summary: str, details: str):
    if details is None:
        return ""
    
    if details == "":
        return ""
    
    return f"""
<details>
<summary>{html.escape(summary, quote=True)}</summary>

{details}

</details>
"""


def md_image(alt_text: str, url: str, width=None):
    if pd.isna(alt_text):
        alt_text = ''
        
    if pd.isna(url):
        return ''
    
    if width is None:
        return f"![{alt_text}]({url})"

    return f'<img src="{url}" alt="{md_table_escape(html.escape(alt_text, quote=True))}" width="{width}" />'


def md_table(df: pd.DataFrame):
    table = df.to_markdown(index=False)
    table = more_than_one_space.sub(' ', table) # Consolidate spaces into two
    table = more_than_three_hyphens.sub('---', table) # Consolidate dashes into three
    return table


def md_truncated_table(df: pd.DataFrame, initial: int = 10, text="View all"):
    if (len(df) <= initial):
        return md_table(df)
    
    head = df.head(initial)
    tail = df.tail(-1 * initial)

    return "\n".join([
        md_table(head),
        "",
        md_summary_details(text, md_table(tail))
    ])


def empty_header(n: int):
    # Zero-width spaces
    return u"\u200B" * n


def md_table_escape(text: str):
    # Hack, since we do not expect this to be common. | will break to the next cell unless it is escaped
    return text.replace('|', '\|')