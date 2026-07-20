"""Dataset summary statistics."""

from typing import Any

from fastapi import APIRouter, Depends
from psycopg2.extensions import connection as PgConnection

from src.api.deps import get_db

_SQL = """
    SELECT
        (SELECT count(*) FROM serving.fact_prices) AS observations,
        (SELECT count(price_mad) FROM serving.fact_prices) AS priced,
        (SELECT count(DISTINCT product_key) FROM serving.fact_prices)
            AS products_with_data,
        (SELECT count(*) FROM serving.dim_source) AS sources,
        (SELECT min(t.year) FROM serving.fact_prices f
            JOIN serving.dim_time t ON f.time_key = t.time_key) AS first_year,
        (SELECT max(t.year) FROM serving.fact_prices f
            JOIN serving.dim_time t ON f.time_key = t.time_key) AS last_year
"""

router = APIRouter(tags=["stats"])


@router.get("/stats")
def stats(db: PgConnection = Depends(get_db)) -> dict[str, Any]:
    """Top-level dataset counts and coverage."""
    with db.cursor() as cur:
        cur.execute(_SQL)
        cols = [c[0] for c in cur.description]
        row = cur.fetchone()
    return dict(zip(cols, row, strict=True)) if row else {}
