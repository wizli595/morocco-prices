"""Product catalog endpoints."""

from typing import Any

from fastapi import APIRouter, Depends
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor

from src.api.deps import get_db

router = APIRouter(tags=["products"])

_SQL = """
    SELECT p.product_id, p.category, p.subcategory, p.product_name,
           count(f.observation_id) AS observations,
           min(t.year) AS first_year, max(t.year) AS last_year
    FROM serving.dim_product p
    LEFT JOIN serving.fact_prices f ON f.product_key = p.product_key
    LEFT JOIN serving.dim_time t ON f.time_key = t.time_key
    GROUP BY p.product_id, p.category, p.subcategory, p.product_name
    ORDER BY observations DESC, p.product_id
"""


@router.get("/products")
def list_products(
    with_data: bool = False, db: PgConnection = Depends(get_db)
) -> dict[str, Any]:
    """Product catalog with data-availability counts."""
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(_SQL)
        rows = [dict(r) for r in cur.fetchall()]
    if with_data:
        rows = [r for r in rows if r["observations"] > 0]
    return {"count": len(rows), "results": rows}
