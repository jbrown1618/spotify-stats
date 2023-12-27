import os
from dotenv import load_dotenv

settings = {}
loaded = False


def get_setting(setting_key, default):
    global loaded

    if setting_key in settings:
        return settings[setting_key]

    if not loaded:
        load_dotenv()
        loaded = True
    
    value = os.getenv(setting_key)

    if isinstance(default, bool) and value is not None:
        value = (value.lower() == "true")

    if isinstance(default, int) and value is not None:
        value = int(value)

    settings[setting_key] = value if value is not None else default

    return settings[setting_key]


def output_dir() -> str:
    return get_setting("OUTPUT_DIR", "./output")


def spotify_client_id() -> str:
    return get_setting("SPOTIFY_CLIENT_ID", None)
    

def spotify_client_secret() -> str:
    return get_setting("SPOTIFY_CLIENT_SECRET", None)


def musicbrainz_useragent() -> str:
    return get_setting("MUSICBRAINZ_USERAGENT", "jbrown1618/spotify-stats")


def musicbrainz_version() -> str:
    return get_setting("MUSIVBRAINZ_VERSION", "1.0.0")


def musicbrainz_contact() -> str:
    return get_setting("MUSICBRAINZ_CONTACT", "https://github.com/jbrown1618/spotify-stats")


def musicbrainz_max_tracks_per_run() -> str:
    return get_setting("MUSICBRAINZ_MAX_TRACKS_PER_RUN", 100)


def musicbrainz_save_batch_size() -> str:
    return get_setting("MUSICBRAINZ_SAVE_BATCH_SIZE", 100)


def should_save_spotify_data() -> bool:
    return get_setting("SAVE_SPOTIFY_DATA", True)


def should_save_supplemental_data() -> bool:
    return get_setting("SAVE_SUPPLEMENTAL_DATA", True)


def should_generate_output() -> bool:
    return get_setting("GENERATE_OUTPUT", True)


def skip_figures() -> bool:
    return get_setting("SKIP_FIGURES", False)


def figure_dpi() -> int:
    return get_setting("FIGURE_DPI", 50)


def should_clear_markdown() -> bool:
    return get_setting("GENERATE_ONLY_PAGE", None) == None


def should_generate_page(page_type: str) -> bool:
    page = get_setting("GENERATE_ONLY_PAGE", None)
    return page == None \
        or page.lower() == page_type.lower() \
        or (page.lower() + 's') == page_type.lower()\
        or page.lower() == (page_type.lower() + 's')
