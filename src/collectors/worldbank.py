"""World Bank API collector for CPI and inflation data."""

from datetime import UTC, datetime
from typing import Any

import structlog

from src.adapters.http.api_client import fetch_json
from src.core.models.enums import CollectionMethod, Confidence, Precision
from src.core.models.observation import RawObservation
from src.core.ports.collector import BaseCollector
from src.core.registry import register_collector

logger = structlog.get_logger()

BASE_URL = "https://api.worldbank.org/v2/country/MAR/indicator"

INDICATORS = {
    "FP.CPI.TOTL": ("CPI-NATIONAL", "index_point", "CPI 2010=100"),
    "FP.CPI.TOTL.ZG": ("INFLATION-NATIONAL", "percent", "Inflation annual %"),
}


@register_collector("worldbank")
class WorldBankCollector(BaseCollector):
    """Fetch CPI and inflation from World Bank API."""

    @property
    def source_id(self) -> str:
        return "WORLDBANK"

    @property
    def source_name(self) -> str:
        return "World Bank Open Data"

    def collect(self) -> list[RawObservation]:
        """Fetch all indicators for Morocco."""
        observations: list[RawObservation] = []
        for code, (product_id, unit, _desc) in INDICATORS.items():
            rows = _fetch_indicator(code)
            for row in rows:
                obs = _parse_row(row, product_id, unit, code)
                if obs:
                    observations.append(obs)
            logger.info(
                "collector.fetch.complete",
                source="WORLDBANK",
                indicator=code,
                records=len(rows),
            )
        return observations

    def check_freshness(self) -> datetime | None:
        return None


def _fetch_indicator(code: str) -> list[dict[str, Any]]:
    """Call World Bank API, return data rows."""
    url = f"{BASE_URL}/{code}"
    params = {"format": "json", "date": "1960:2025", "per_page": "200"}
    data = fetch_json(url, params=params, source="WORLDBANK")
    if not isinstance(data, list) or len(data) < 2:
        return []
    return [r for r in data[1] if r.get("value") is not None]


def _parse_row(
    row: dict[str, Any],
    product_id: str,
    unit: str,
    code: str,
) -> RawObservation | None:
    """Convert one API row to a RawObservation."""
    value = row.get("value")
    if value is None:
        return None
    return RawObservation(
        source_id="WORLDBANK",
        product_id=product_id,
        location_id="MA-NATIONAL",
        year=int(row["date"]),
        month=None,
        day=None,
        value=float(value),
        value_min=None,
        value_max=None,
        unit=unit,
        currency="index",
        confidence=Confidence.INSTITUTIONAL,
        precision=Precision.EXACT,
        collection_method=CollectionMethod.API,
        collected_at=datetime.now(tz=UTC),
        raw_metadata={"indicator": code},
    )
