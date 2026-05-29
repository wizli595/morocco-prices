"""Manual collector for hand-entered historical price data."""

import csv
from datetime import datetime, timezone
from pathlib import Path

import structlog

from src.core.models.enums import CollectionMethod, Confidence, Precision
from src.core.models.observation import RawObservation
from src.core.ports.collector import BaseCollector
from src.core.registry import register_collector

logger = structlog.get_logger()

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "manual"


@register_collector("manual")
class ManualCollector(BaseCollector):
    """Read historical anchors from CSV files."""

    @property
    def source_id(self) -> str:
        return "MANUAL"

    @property
    def source_name(self) -> str:
        return "Historical Archives"

    def collect(self) -> list[RawObservation]:
        """Parse all CSV files in data/manual/."""
        observations: list[RawObservation] = []
        for csv_path in DATA_PATH.glob("*.csv"):
            observations.extend(_parse_csv(csv_path))
        logger.info(
            "collector.fetch.complete",
            source="MANUAL", records=len(observations),
        )
        return observations

    def check_freshness(self) -> datetime | None:
        return None


def _parse_csv(path: Path) -> list[RawObservation]:
    """Parse one manual CSV into observations."""
    results: list[RawObservation] = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            results.append(_row_to_observation(row))
    return results


def _row_to_observation(row: dict) -> RawObservation:
    """Convert one CSV row to RawObservation."""
    month = int(row["month"]) if row.get("month") else None
    return RawObservation(
        source_id="MANUAL",
        product_id=row["product_id"],
        location_id="MA-NATIONAL",
        year=int(row["year"]),
        month=month,
        day=None,
        value=float(row["price_value"]),
        value_min=None,
        value_max=None,
        unit=row["unit"],
        currency="MAD",
        confidence=Confidence.ESTIMATED,
        precision=Precision.APPROXIMATE,
        collection_method=CollectionMethod.MANUAL,
        collected_at=datetime.now(tz=timezone.utc),
        raw_metadata={
            "source_document": row.get("source_document", ""),
            "page_reference": row.get("page_reference", ""),
        },
    )
