"""Read price data from PostgreSQL for processing."""

from typing import Any

from psycopg2.extensions import cursor as PgCursor

PRICES_SQL = """
    SELECT
        f.observation_id, p.product_id, l.location_id,
        f.time_key, s.source_id, s.priority_rank,
        f.original_value, f.original_unit, f.original_currency,
        t.year
    FROM serving.fact_prices f
    JOIN serving.dim_product p ON f.product_key = p.product_key
    JOIN serving.dim_location l ON f.location_key = l.location_key
    JOIN serving.dim_source s ON f.source_key = s.source_key
    JOIN serving.dim_time t ON f.time_key = t.time_key
"""

CPI_SQL = """
    SELECT t.year, f.original_value
    FROM serving.fact_prices f
    JOIN serving.dim_product p ON f.product_key = p.product_key
    JOIN serving.dim_time t ON f.time_key = t.time_key
    WHERE p.product_id = 'CPI-NATIONAL'
    ORDER BY t.year
"""


def fetch_all_prices(cur: PgCursor) -> list[dict[str, Any]]:
    """Read all price rows as dicts with float-cast decimals."""
    cur.execute(PRICES_SQL)
    cols = [d[0] for d in cur.description]
    return [_cast_row(dict(zip(cols, row, strict=True))) for row in cur.fetchall()]


def _cast_row(row: dict[str, Any]) -> dict[str, Any]:
    """Cast Decimal fields to float for transformer compatibility."""
    for key in ("original_value",):
        if row.get(key) is not None:
            row[key] = float(row[key])
    return row


def fetch_cpi_series(cur: PgCursor) -> list[tuple[int, float]]:
    """Read CPI series as (year, value) tuples."""
    cur.execute(CPI_SQL)
    return [(int(r[0]), float(r[1])) for r in cur.fetchall()]
