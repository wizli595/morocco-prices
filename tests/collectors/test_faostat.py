"""Tests for the FAOSTAT wide-format parser."""

from src.collectors.faostat_parser import (
    ITEM_CODES,
    is_morocco_row,
    parse_wide_row,
)
from src.core.models.enums import Confidence


def _make_wide_row(
    area_code: str = "143",
    item_code: str = "977",
    element: str = "Producer Price (LCU/tonne)",
    values: dict[str, str] | None = None,
) -> dict:
    """Build a fake FAOSTAT wide-format CSV row."""
    row = {
        "Area Code": area_code,
        "Item Code": item_code,
        "Element": element,
    }
    for year, (value, flag) in (values or {}).items():
        row[f"Y{year}"] = value
        row[f"Y{year}F"] = flag
    return row


def test_is_morocco_row_valid():
    """Should accept a valid Morocco + tracked-item row."""
    assert is_morocco_row(_make_wide_row()) is True


def test_is_morocco_row_wrong_country():
    """Should reject non-Morocco rows."""
    assert is_morocco_row(_make_wide_row(area_code="100")) is False


def test_is_morocco_row_unknown_item():
    """Should reject items not in ITEM_CODES."""
    assert is_morocco_row(_make_wide_row(item_code="9999")) is False


def test_parse_wide_row_sheep_1998():
    """Should unpivot a sheep meat row into a per-year observation."""
    row = _make_wide_row(values={"1998": ("51250", "A")})
    observations = parse_wide_row(row)

    assert len(observations) == 1
    obs = observations[0]
    assert obs.product_id == "MEAT-SHEEP"
    assert obs.year == 1998
    assert obs.value == 51250.0
    assert obs.confidence == Confidence.OFFICIAL


def test_parse_wide_row_estimated_flag():
    """Flag 'E' should give estimated confidence."""
    row = _make_wide_row(values={"1998": ("51250", "E")})
    assert parse_wide_row(row)[0].confidence == Confidence.ESTIMATED


def test_parse_wide_row_skips_empty_years():
    """Only populated year columns should yield observations."""
    row = _make_wide_row(values={"1998": ("51250", "A"), "1999": ("", "")})
    observations = parse_wide_row(row)

    assert len(observations) == 1
    assert observations[0].year == 1998


def test_parse_wide_row_multiple_years():
    """Each populated year should become its own observation."""
    row = _make_wide_row(values={"1998": ("51250", "A"), "1999": ("52000", "A")})
    years = sorted(obs.year for obs in parse_wide_row(row))

    assert years == [1998, 1999]


def test_all_item_codes_mapped():
    """Every ITEM_CODE should map to a valid product_id."""
    for product_id in ITEM_CODES.values():
        assert product_id.startswith(("MEAT-", "DAIRY-", "CEREAL-"))
