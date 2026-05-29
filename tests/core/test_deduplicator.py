"""Tests for deduplicator."""

from src.core.transformers.deduplicator import PriceRow, deduplicate


def _row(source: str, priority: int, value: float = 50.0) -> PriceRow:
    return PriceRow(
        observation_id=f"{source}-001",
        product_id="MEAT-SHEEP",
        location_id="MA-NATIONAL",
        time_key=19700000,
        source_id=source,
        value=value,
        priority=priority,
    )


def test_no_duplicates():
    rows = [_row("A", 1), _row("B", 2, value=60.0)]
    rows[1].time_key = 19850000
    result = deduplicate(rows)
    assert len(result) == 2


def test_keeps_higher_priority():
    """Priority 1 (HCP) should win over priority 3 (World Bank)."""
    rows = [_row("WORLDBANK", 3), _row("HCP", 1, value=55.0)]
    result = deduplicate(rows)
    assert len(result) == 1
    assert result[0].source_id == "HCP"


def test_empty_input():
    assert deduplicate([]) == []
