"""FAOSTAT Consumer Price Indices collector — Morocco monthly food CPI."""

import codecs
import csv
import io
import zipfile
from datetime import UTC, datetime

import structlog

from src.adapters.http.api_client import download_bytes
from src.core.models.enums import CollectionMethod, Confidence, Precision
from src.core.models.observation import RawObservation
from src.core.ports.collector import BaseCollector
from src.core.registry import register_collector

logger = structlog.get_logger()

BULK_URL = (
    "https://bulks-faostat.fao.org/production/"
    "ConsumerPriceIndices_E_All_Data_(Normalized).zip"
)
MOROCCO_CODE = "143"
FOOD_INDEX_ITEM = "23013"  # Consumer Prices, Food Indices (2015 = 100)
MONTHS = {
    m: i + 1
    for i, m in enumerate(
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
    )
}


@register_collector("faostat_cp")
class FAOSTATConsumerPriceCollector(BaseCollector):
    """Fetch Morocco's monthly food consumer price index from FAOSTAT."""

    @property
    def source_id(self) -> str:
        return "FAOSTAT"

    @property
    def source_name(self) -> str:
        return "FAOSTAT Consumer Price Indices"

    def collect(self) -> list[RawObservation]:
        """Download the CP bulk zip and parse Morocco food-index rows."""
        raw = download_bytes(BULK_URL, timeout=300, source="FAOSTAT")
        observations = _extract_food_cpi(raw)
        logger.info(
            "collector.fetch.complete",
            source="FAOSTAT",
            dataset="consumer_price_indices",
            records=len(observations),
        )
        return observations

    def check_freshness(self) -> None:
        return None


def _extract_food_cpi(zip_bytes: bytes) -> list[RawObservation]:
    """Unzip and parse the normalized CP CSV into food-index observations."""
    results: list[RawObservation] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        csv_name = next(n for n in zf.namelist() if n.endswith(".csv"))
        with zf.open(csv_name) as f:
            reader = csv.DictReader(codecs.iterdecode(f, "utf-8-sig"))
            for row in reader:
                obs = parse_cp_row(row)
                if obs:
                    results.append(obs)
    return results


def parse_cp_row(row: dict[str, str]) -> RawObservation | None:
    """Convert one CP row into a monthly food-index observation."""
    if row.get("Area Code") != MOROCCO_CODE or row.get("Item Code") != FOOD_INDEX_ITEM:
        return None
    month = MONTHS.get(row.get("Months", ""))
    value = row.get("Value", "")
    if not month or not value:
        return None
    return RawObservation(
        source_id="FAOSTAT",
        product_id="CPI-FOOD",
        location_id="MA-NATIONAL",
        year=int(row["Year"]),
        month=month,
        day=None,
        value=float(value),
        value_min=None,
        value_max=None,
        unit="index_point",
        currency="index",
        confidence=_flag_to_confidence(row.get("Flag", "")),
        precision=Precision.EXACT,
        collection_method=CollectionMethod.FILE_DOWNLOAD,
        collected_at=datetime.now(tz=UTC),
        raw_metadata={"item_code": FOOD_INDEX_ITEM, "flag": row.get("Flag", "")},
    )


def _flag_to_confidence(flag: str) -> Confidence:
    if flag in ("A", ""):
        return Confidence.OFFICIAL
    if flag == "E":
        return Confidence.ESTIMATED
    return Confidence.INSTITUTIONAL
