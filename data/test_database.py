import unittest
from unittest.mock import patch

from data import database


class DatabaseURLTests(unittest.TestCase):
    def test_engine_accepts_postgres_schemes(self):
        suffix = "demo:password@localhost:5432/example?sslmode=require"
        schemes = (
            ("postgres://", "postgresql+psycopg2://"),
            ("postgresql://", "postgresql://"),
            ("postgresql+psycopg2://", "postgresql+psycopg2://"),
        )
        for supplied, expected in schemes:
            with self.subTest(scheme=supplied):
                with (
                    patch.object(database, "_engine", None),
                    patch.object(database, "postgres_url", return_value=supplied + suffix),
                    patch.object(database.sqlalchemy, "create_engine") as create_engine,
                ):
                    engine = database.get_engine()
                    self.assertIs(engine, create_engine.return_value)
                    self.assertIs(database.get_engine(), engine)
                    create_engine.assert_called_once_with(expected + suffix)

    def test_direct_connection_preserves_standard_and_legacy_urls(self):
        for scheme in ("postgres://", "postgresql://"):
            url = scheme + "demo:password@localhost:5432/example"
            with self.subTest(scheme=scheme):
                with (
                    patch.object(database, "postgres_url", return_value=url),
                    patch.object(database.psycopg2, "connect") as connect,
                ):
                    self.assertIs(database.get_connection(), connect.return_value)
                    connect.assert_called_once_with(url, sslmode="require")


if __name__ == "__main__":
    unittest.main()
