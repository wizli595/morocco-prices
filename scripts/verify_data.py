"""Verify raw observations against the quality rules before cleaning."""

import structlog
from psycopg2.extras import RealDictCursor

from scripts.db import get_connection
from src.core.quality.validator import validate

logger = structlog.get_logger()

_SQL = """
    SELECT f.observation_id, p.product_id, t.year, t.month,
           f.original_value AS value, f.original_unit AS unit,
           f.original_currency AS currency, f.confidence,
           f.precision, f.collection_method
    FROM serving.fact_prices f
    JOIN serving.dim_product p ON f.product_key = p.product_key
    JOIN serving.dim_time t ON f.time_key = t.time_key
"""


def run() -> None:
    """Load observations and run the quality validator."""
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(_SQL)
        rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    for row in rows:
        if row["value"] is not None:
            row["value"] = float(row["value"])

    report = validate(rows)
    for failure in report.failures:
        logger.warning("quality.failure", detail=failure)
    logger.info(
        "quality.complete",
        total=report.total,
        failures=len(report.failures),
        verdict="PASS" if report.passed else "FAIL",
    )
    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
