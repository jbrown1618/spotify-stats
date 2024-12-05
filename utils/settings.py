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


def postgres_url() -> str:
    return get_setting("DATABASE_URL", None)


def postgres_host() -> str:
    return get_setting("POSTGRES_HOST", "127.0.0.1")


def postgres_user() -> str:
    return get_setting("POSTGRES_USER", "postgres")


def postgres_password() -> str:
    return get_setting("POSTGRES_PASS", "password")


def postgres_port() -> str:
    return get_setting("POSTGRES_PORT", 5432)


def data_mode() -> str:
    if postgres_url() is not None:
        return "sql"

    return get_setting("DATA_MODE", "csv").lower()


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


def musicbrainz_max_tracks_per_run() -> int:
    return get_setting("MUSICBRAINZ_MAX_TRACKS_PER_RUN", 100)


def musicbrainz_save_batch_size() -> int:
    return get_setting("MUSICBRAINZ_SAVE_BATCH_SIZE", 100)


def musicbrainz_retry_days() -> int:
    return get_setting("MUSICBRAINZ_RETRY_DAYS", 60)


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
        or page == '' \
        or page.lower() == page_type.lower() \
        or (page.lower() + 's') == page_type.lower()\
        or page.lower() == (page_type.lower() + 's')
