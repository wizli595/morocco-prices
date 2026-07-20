"""Export the denormalized gold dataset to CSV for publishing."""

import csv
from pathlib import Path

import structlog

from scripts.db import get_connection

logger = structlog.get_logger()

OUT_PATH = Path(__file__).parent.parent / "data" / "gold" / "morocco_prices.csv"

_SQL = """
    SELECT p.product_id, p.category, p.product_name,
           l.location_id, t.year, t.month,
           f.original_value, f.original_unit, f.original_currency,
           f.price_mad, f.price_usd, f.price_real_mad,
           f.confidence, f.precision, f.collection_method, s.source_id
    FROM serving.fact_prices f
    JOIN serving.dim_product p ON f.product_key = p.product_key
    JOIN serving.dim_location l ON f.location_key = l.location_key
    JOIN serving.dim_time t ON f.time_key = t.time_key
    JOIN serving.dim_source s ON f.source_key = s.source_key
    ORDER BY p.product_id, t.year, t.month
"""


def run() -> None:
    """Materialize the joined dataset as a single CSV."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SQL)
    cols = [c[0] for c in cur.description]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with OUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(cols)
        for row in cur:
            writer.writerow(row)
            rows += 1

    cur.close()
    conn.close()
    logger.info("export.complete", rows=rows, path=str(OUT_PATH))


if __name__ == "__main__":
    run()
