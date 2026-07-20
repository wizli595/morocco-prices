"""API dependencies — per-request database access."""

from collections.abc import Iterator

import psycopg2
from psycopg2.extensions import connection as PgConnection

from src.config import Settings


def get_db() -> Iterator[PgConnection]:
    """Yield a PostgreSQL connection, closed after the request."""
    settings = Settings()
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        dbname=settings.postgres_db,
    )
    try:
        yield conn
    finally:
        conn.close()
