import psycopg2
import sqlalchemy

from utils.settings import (
    postgres_host,
    postgres_password,
    postgres_port,
    postgres_url,
    postgres_user,
)


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = postgres_url()
        if url is not None:
            print("Connecting to Postgres via DATABASE_URL")
            if url.startswith("postgres") and not url.startswith("postgresql+psycopg2"):
                url = "postgresql+psycopg2" + url[len("postgres") :]
            _engine = sqlalchemy.create_engine(url)
        else:
            print("Connecting to local Postgres instance: " + postgres_host())
            _engine = sqlalchemy.create_engine(
                f"postgresql+psycopg2://{postgres_user()}:{postgres_password()}"
                f"@{postgres_host()}/spotifystats"
            )
    return _engine


_displayed_connection = False


def get_connection():
    global _displayed_connection
    url = postgres_url()
    if url is not None:
        if not _displayed_connection:
            print("Connecting to Postgres via DATABASE_URL")
            _displayed_connection = True
        return psycopg2.connect(url, sslmode="require")

    if not _displayed_connection:
        print("Connecting to local Postgres instance: " + postgres_host())
        _displayed_connection = True
    return psycopg2.connect(
        database="spotifystats",
        host=postgres_host(),
        user=postgres_user(),
        password=postgres_password(),
        port=postgres_port(),
    )
