"""Tests for the World Bank collector."""

from unittest.mock import patch

from src.collectors.worldbank import WorldBankCollector, _parse_row


def test_worldbank_source_id():
    """Should identify as WORLDBANK."""
    collector = WorldBankCollector()
    assert collector.source_id == "WORLDBANK"


def test_parse_row_valid():
    """Should parse a valid API row."""
    row = {"date": "2020", "value": 105.3}
    obs = _parse_row(row, "CPI-NATIONAL", "index_point", "FP.CPI.TOTL")

    assert obs is not None
    assert obs.year == 2020
    assert obs.value == 105.3
    assert obs.product_id == "CPI-NATIONAL"
    assert obs.location_id == "MA-NATIONAL"


def test_parse_row_null_value():
    """Should return None for null value rows."""
    row = {"date": "2020", "value": None}
    obs = _parse_row(row, "CPI-NATIONAL", "index_point", "FP.CPI.TOTL")

    assert obs is None


def test_worldbank_registered():
    """Should be in the collector registry."""
    from src.core.registry import get_collector

    cls = get_collector("worldbank")
    assert cls is WorldBankCollector
