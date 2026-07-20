"""Shared database connection for scripts, backed by application settings."""

import psycopg2
from psycopg2.extensions import connection as PgConnection

from src.config import Settings


def get_connection() -> PgConnection:
    """Open a PostgreSQL connection using the single source of config."""
    settings = Settings()
    return psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        dbname=settings.postgres_db,
    )
