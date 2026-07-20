"""Tests for the Selina Wamucii scraper parser."""

from src.collectors.selina_parser import parse_price
from src.core.models.enums import CollectionMethod
from src.core.registry import get_collector

_HTML = """
<html><body>
  <h1>Beef Price in Morocco, July 2026</h1>
  <span class="swpc-price-value">US$11.2942/ kg</span>
</body></html>
"""


def test_parses_price_and_date():
    obs = parse_price(_HTML, "MEAT-BEEF")
    assert obs is not None
    assert obs.value == 11.2942
    assert obs.unit == "USD/kg"
    assert obs.currency == "USD"
    assert obs.year == 2026
    assert obs.month == 7
    assert obs.collection_method == CollectionMethod.SCRAPE


def test_missing_price_returns_none():
    assert parse_price("<html><body><h1>x</h1></body></html>", "MEAT-BEEF") is None


def test_registered_in_registry():
    import src.collectors  # noqa: F401

    assert get_collector("selina").__name__ == "SelinaCollector"
