"""Tests for the Numbeo food-prices parser (one page, many products)."""

from src.collectors.numbeo_parser import parse_food_table
from src.core.models.enums import CollectionMethod
from src.core.registry import get_collector

_HTML = """
<html><body><table class="data_wide_table">
  <tr><td>Milk (Regular, 1 Liter)</td><td>8.52&nbsp;MAD</td></tr>
  <tr><td>White Rice (1 kg)</td><td>16.48&nbsp;MAD</td></tr>
  <tr><td>Chicken Fillets (1 kg)</td><td>57.85&nbsp;MAD</td></tr>
  <tr><td>Tomato (1 kg)</td><td>7.42&nbsp;MAD</td></tr>
</table></body></html>
"""


def test_parses_multiple_mapped_rows():
    obs = parse_food_table(_HTML)
    ids = {o.product_id for o in obs}
    # rice, chicken, tomato map; milk is not in ITEM_MAP (per-litre, skipped)
    assert ids == {"CEREAL-RICE-ROUND", "MEAT-CHICKEN-BROILER", "VEG-TOMATO"}


def test_values_and_method():
    rice = next(
        o for o in parse_food_table(_HTML) if o.product_id == "CEREAL-RICE-ROUND"
    )
    assert rice.value == 16.48
    assert rice.unit == "MAD/kg"
    assert rice.collection_method == CollectionMethod.SCRAPE


def test_empty_table_yields_nothing():
    assert parse_food_table("<html><body></body></html>") == []


def test_registered():
    import src.collectors  # noqa: F401

    assert get_collector("numbeo").__name__ == "NumbeoCollector"
