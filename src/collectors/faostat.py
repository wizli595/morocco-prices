"""FAOSTAT bulk CSV collector for producer prices."""

import csv
import io
import zipfile
from datetime import datetime, timezone

import structlog

from src.adapters.http.api_client import download_bytes
from src.collectors.faostat_parser import is_morocco_price_row, parse_row
from src.core.models.observation import RawObservation
from src.core.ports.collector import BaseCollector
from src.core.registry import register_collector

logger = structlog.get_logger()

BULK_URL = "https://bulks-faostat.fao.org/production/Prices_E_All_Data_NOFLAG.zip"


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
        """Download, unzip, parse Morocco rows."""
        logger.info("collector.fetch.start", source="FAOSTAT")
        raw = download_bytes(BULK_URL, timeout=300, source="FAOSTAT")
        rows = _extract_csv_rows(raw)
        observations = _filter_and_parse(rows)
        logger.info(
            "collector.fetch.complete",
            source="FAOSTAT", records=len(observations),
        )
        return observations

    def check_freshness(self) -> datetime | None:
        return None


def _extract_csv_rows(zip_bytes: bytes) -> list[dict]:
    """Unzip and read CSV into list of dicts."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        csv_name = [n for n in zf.namelist() if n.endswith(".csv")][0]
        with zf.open(csv_name) as f:
            text = io.TextIOWrapper(f, encoding="utf-8")
            return list(csv.DictReader(text))


def _filter_and_parse(rows: list[dict]) -> list[RawObservation]:
    """Keep only Morocco price rows and parse them."""
    return [parse_row(r) for r in rows if is_morocco_price_row(r)]
