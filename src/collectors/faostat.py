"""FAOSTAT bulk CSV collector for producer prices."""

import csv
import io
import zipfile

import structlog

from src.adapters.http.api_client import download_bytes
from src.collectors.faostat_parser import is_morocco_row, parse_wide_row
from src.core.models.observation import RawObservation
from src.core.ports.collector import BaseCollector
from src.core.registry import register_collector

logger = structlog.get_logger()

BULK_URL = "https://bulks-faostat.fao.org/production/Prices_E_All_Data.zip"


@register_collector("faostat")
class FAOSTATCollector(BaseCollector):
    """Download FAOSTAT bulk CSV and extract Morocco prices."""

    @property
    def source_id(self) -> str:
        return "FAOSTAT"

    @property
    def source_name(self) -> str:
        return "FAOSTAT Producer Prices"

    def collect(self) -> list[RawObservation]:
        """Download, unzip, filter Morocco, unpivot years."""
        logger.info("collector.fetch.start", source="FAOSTAT")
        raw = download_bytes(BULK_URL, timeout=300, source="FAOSTAT")
        observations = _extract_and_parse(raw)
        logger.info(
            "collector.fetch.complete",
            source="FAOSTAT",
            records=len(observations),
        )
        return observations

    def check_freshness(self) -> None:
        return None


def _extract_and_parse(zip_bytes: bytes) -> list[RawObservation]:
    """Unzip, read wide CSV, filter and unpivot Morocco rows."""
    results: list[RawObservation] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        csv_name = next(n for n in zf.namelist() if n.endswith(".csv"))
        with zf.open(csv_name) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
            for row in reader:
                if is_morocco_row(row):
                    results.extend(parse_wide_row(row))
    return results
