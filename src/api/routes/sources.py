"""Data source endpoints."""

from typing import Any

from fastapi import APIRouter, Depends
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor

from src.api.deps import get_db

router = APIRouter(tags=["sources"])

_SQL = """
    SELECT s.source_id, s.source_name, s.organization, s.reliability,
           s.priority_rank, count(f.observation_id) AS observations
    FROM serving.dim_source s
    LEFT JOIN serving.fact_prices f ON f.source_key = s.source_key
    GROUP BY s.source_id, s.source_name, s.organization,
             s.reliability, s.priority_rank
    ORDER BY s.priority_rank
"""


@router.get("/sources")
def list_sources(db: PgConnection = Depends(get_db)) -> dict[str, Any]:
    """All sources with observation counts."""
    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(_SQL)
        rows = [dict(r) for r in cur.fetchall()]
    return {"count": len(rows), "results": rows}
