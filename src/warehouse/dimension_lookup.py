"""Look up dimension surrogate keys from natural keys."""

from psycopg2.extensions import cursor as PgCursor


def get_product_key(cur: PgCursor, product_id: str) -> int | None:
    """Find product surrogate key by product_id."""
    cur.execute(
        "SELECT product_key FROM serving.dim_product WHERE product_id = %s",
        (product_id,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_location_key(cur: PgCursor, location_id: str) -> int | None:
    """Find location surrogate key by location_id."""
    cur.execute(
        "SELECT location_key FROM serving.dim_location WHERE location_id = %s",
        (location_id,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_source_key(cur: PgCursor, source_id: str) -> int | None:
    """Find source surrogate key by source_id."""
    cur.execute(
        "SELECT source_key FROM serving.dim_source WHERE source_id = %s",
        (source_id,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_time_key(year: int, month: int | None) -> int:
    """Build time_key integer from year and optional month."""
    m = month or 0
    return year * 10000 + m * 100
