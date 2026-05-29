"""Tests for the FAOSTAT collector and parser."""

from src.collectors.faostat_parser import (
    ITEM_CODES,
    is_morocco_price_row,
    parse_row,
)
from src.core.models.enums import Confidence


def _make_row(
    area_code: str = "143",
    item_code: str = "977",
    value: str = "51250",
    year: str = "1998",
    flag: str = "A",
) -> dict:
    """Build a fake FAOSTAT CSV row."""
    return {
        "Area Code": area_code,
        "Item Code": item_code,
        "Value": value,
        "Year": year,
        "Element": "Producer Price (LCU/tonne)",
        "Flag": flag,
    }


def test_is_morocco_price_row_valid():
    """Should accept a valid Morocco price row."""
    assert is_morocco_price_row(_make_row()) is True


def test_is_morocco_price_row_wrong_country():
    """Should reject non-Morocco rows."""
    assert is_morocco_price_row(_make_row(area_code="100")) is False


def test_is_morocco_price_row_unknown_item():
    """Should reject items not in ITEM_CODES."""
    assert is_morocco_price_row(_make_row(item_code="9999")) is False


def test_is_morocco_price_row_empty_value():
    """Should reject rows with empty value."""
    assert is_morocco_price_row(_make_row(value="")) is False


def test_parse_row_sheep_1998():
    """Should parse a sheep meat row correctly."""
    row = _make_row(value="51250", year="1998", flag="A")
    obs = parse_row(row)

    assert obs.product_id == "MEAT-SHEEP"
    assert obs.year == 1998
    assert obs.value == 51250.0
    assert obs.confidence == Confidence.OFFICIAL


def test_parse_row_estimated_flag():
    """Flag 'E' should give estimated confidence."""
    obs = parse_row(_make_row(flag="E"))
    assert obs.confidence == Confidence.ESTIMATED


def test_all_item_codes_mapped():
    """Every ITEM_CODE should map to a valid product_id."""
    for code, product_id in ITEM_CODES.items():
        assert product_id.startswith(("MEAT-", "DAIRY-", "CEREAL-"))
