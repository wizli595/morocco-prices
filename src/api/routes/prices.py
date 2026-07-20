"""Price observation endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Query
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor

from src.api.deps import get_db

router = APIRouter(tags=["prices"])

_LIST_SQL = """
    SELECT p.product_id, p.category, l.location_id, t.year, t.month,
           f.original_value, f.original_unit, f.original_currency,
           f.price_mad, f.price_usd, f.price_real_mad, f.confidence, s.source_id
    FROM serving.fact_prices f
    JOIN serving.dim_product p ON f.product_key = p.product_key
    JOIN serving.dim_location l ON f.location_key = l.location_key
    JOIN serving.dim_time t ON f.time_key = t.time_key
    JOIN serving.dim_source s ON f.source_key = s.source_key
    WHERE (%(product_id)s IS NULL OR p.product_id = %(product_id)s)
      AND (%(source_id)s IS NULL OR s.source_id = %(source_id)s)
      AND (%(year_from)s IS NULL OR t.year >= %(year_from)s)
      AND (%(year_to)s IS NULL OR t.year <= %(year_to)s)
    ORDER BY p.product_id, t.year, t.month
    LIMIT %(limit)s OFFSET %(offset)s
"""

_SERIES_SQL = """
    SELECT t.year, t.month, f.price_mad, f.price_usd, s.source_id, f.confidence
    FROM serving.fact_prices f
    JOIN serving.dim_product p ON f.product_key = p.product_key
    JOIN serving.dim_time t ON f.time_key = t.time_key
    JOIN serving.dim_source s ON f.source_key = s.source_key
    WHERE p.product_id = %(product_id)s AND f.price_mad IS NOT NULL
    ORDER BY t.year, t.month
"""

_DECIMAL_COLS = ("original_value", "price_mad", "price_usd", "price_real_mad")


def _floatify(row: dict[str, Any]) -> dict[str, Any]:
    """Cast Decimal columns to float for JSON serialization."""
    for col in _DECIMAL_COLS:
        if row.get(col) is not None:
            row[col] = float(row[col])
    return row


@router.get("/prices")
def list_prices(
    product_id: str | None = None,
    source_id: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: PgConnection = Depends(get_db),
) -> dict[str, Any]:
    """Filtered, paginated price observations."""
    params = {
        "product_id": product_id,
        "source_id": source_id,
        "year_from": year_from,
        "year_to": year_to,
        "limit": limit,
        "offset": offset,
    }
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(_LIST_SQL, params)
        rows = [_floatify(dict(r)) for r in cur.fetchall()]
    return {"count": len(rows), "limit": limit, "offset": offset, "results": rows}


@router.get("/prices/{product_id}/timeseries")
def timeseries(product_id: str, db: PgConnection = Depends(get_db)) -> dict[str, Any]:
    """Full normalized MAD/kg time series for one product."""
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(_SERIES_SQL, {"product_id": product_id})
        rows = [_floatify(dict(r)) for r in cur.fetchall()]
    return {"product_id": product_id, "points": len(rows), "series": rows}
