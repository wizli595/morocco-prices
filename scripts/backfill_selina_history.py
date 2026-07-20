"""Backfill documented historical Selina export prices into the warehouse.

Reads data/backfill/selina_history.csv (real figures from the research docs)
and inserts them as historical SELINA observations for the gap trend.
"""

import csv
from datetime import UTC, datetime
from pathlib import Path

import structlog

from scripts.db import get_connection
from src.core.models.enums import CollectionMethod, Confidence, Precision
from src.core.models.observation import RawObservation
from src.warehouse.insert_observation import insert_observation

logger = structlog.get_logger()

CSV_PATH = Path(__file__).parent.parent / "data" / "backfill" / "selina_history.csv"


def _to_observation(row: dict[str, str]) -> RawObservation:
    return RawObservation(
        source_id="SELINA",
        product_id=row["product_id"],
        location_id="MA-NATIONAL",
        year=int(row["year"]),
        month=None,
        day=None,
        value=float(row["usd_per_kg"]),
        value_min=None,
        value_max=None,
        unit="USD/kg",
        currency="USD",
        confidence=Confidence.ESTIMATED,
        precision=Precision.APPROXIMATE,
        collection_method=CollectionMethod.SCRAPE,
        collected_at=datetime.now(tz=UTC),
        raw_metadata={"backfill": "true", "note": row["source_note"]},
    )


def run() -> None:
    """Insert every historical row from the CSV."""
    conn = get_connection()
    cur = conn.cursor()
    with CSV_PATH.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    inserted = sum(
        insert_observation(cur, _to_observation(r), "backfill_selina") for r in rows
    )
    conn.commit()
    cur.close()
    conn.close()
    logger.info("backfill.complete", source="SELINA", rows=len(rows), inserted=inserted)


if __name__ == "__main__":
    run()
