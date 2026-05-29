"""Shared database connection for seed scripts."""

import os

import psycopg2


def get_connection():
    """Create PostgreSQL connection from env vars."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        user=os.getenv("POSTGRES_USER", "maprix"),
        password=os.getenv("POSTGRES_PASSWORD", "changeme"),
        dbname=os.getenv("POSTGRES_DB", "maprix"),
    )
