"""Tests for the FAOSTAT consumer-price-index (food) collector."""

from src.collectors.faostat_cp import parse_cp_row
from src.core.models.enums import CollectionMethod, Confidence
from src.core.registry import get_collector


def _row(area="143", item="23013", months="June", year="2024", value="131.7", flag="X"):
    return {
        "Area Code": area,
        "Item Code": item,
        "Months": months,
        "Year": year,
        "Value": value,
        "Flag": flag,
    }


def test_parses_morocco_food_index():
    obs = parse_cp_row(_row())
    assert obs is not None
    assert obs.product_id == "CPI-FOOD"
    assert obs.year == 2024
    assert obs.month == 6
    assert obs.value == 131.7
    assert obs.unit == "index_point"
    assert obs.collection_method == CollectionMethod.FILE_DOWNLOAD


def test_rejects_non_morocco():
    assert parse_cp_row(_row(area="100")) is None


def test_rejects_non_food_index_item():
    assert parse_cp_row(_row(item="23012")) is None  # general index, not food


def test_rejects_empty_value():
    assert parse_cp_row(_row(value="")) is None


def test_flag_x_is_institutional():
    assert parse_cp_row(_row(flag="X")).confidence == Confidence.INSTITUTIONAL


def test_registered_in_plugin_registry():
    import src.collectors  # noqa: F401

    assert get_collector("faostat_cp").__name__ == "FAOSTATConsumerPriceCollector"
