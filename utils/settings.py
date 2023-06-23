import os
from dotenv import load_dotenv

settings = {
    "output_dir": "./output",
    "spotify_client_id": "",
    "spotify_client_secret": "",
    "skip_data_fetching": False,
    "skip_figures": False,
}


def init_settings():
    load_dotenv()
    set_output_dir(os.getenv("OUTPUT_DIR"))
    set_spotify_client_id(os.getenv("SPOTIPY_CLIENT_ID"))
    set_spotify_client_secret(os.getenv("SPOTIPY_CLIENT_SECRET"))
    set_skip_data_fetching(os.getenv("SKIP_DATA_FETCHING") is not None and os.getenv("SKIP_DATA_FETCHING") != "False")
    set_skip_figures(os.getenv("SKIP_FIGURES") is not None and os.getenv("SKIP_FIGURES") != "False")
    set_generate_only_page(os.getenv("GENERATE_ONLY_PAGE"))


def set_output_dir(output_dir: str):
    settings["output_dir"] = output_dir


def output_dir() -> str:
    return settings["output_dir"]


def set_spotify_client_id(id: str):
    settings["spotify_client_id"] = id


def spotify_client_id() -> str:
    return settings["spotify_client_id"]


def set_spotify_client_secret(secret: str):
    settings["spotify_client_secret"] = secret
    

def spotify_client_secret() -> str:
    return settings["spotify_client_secret"]


def set_skip_data_fetching(skip: bool):
    settings["skip_data_fetching"] = skip


def skip_data_fetching() -> bool:
    return settings["skip_data_fetching"]


def set_skip_figures(skip: bool):
    settings["skip_figures"] = skip


def skip_figures() -> bool:
    return settings["skip_figures"]


def should_clear_markdown() -> bool:
    return settings["generate_only_page"] == None


def should_generate_page(page_type: str) -> bool:
    return settings["generate_only_page"] == None or settings["generate_only_page"].lower() == page_type.lower()


def set_generate_only_page(page_type: str):
    settings["generate_only_page"] = page_type
