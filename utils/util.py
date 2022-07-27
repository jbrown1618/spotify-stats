import re


def get_id(uri: str):
    last_colon = uri.rindex(":") + 1
    return uri[last_colon:]


def md_link(text: str, url: str):
    return f"[{text}]({url})"


def file_name_friendly(text: str):
    return re.sub(r"[^a-z0-9]", "_", text.lower())