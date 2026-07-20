"""Tests for the core quality rules and validator."""

from typing import Any

import pytest

from src.core.models.errors import QualityCheckFailed
from src.core.quality.validator import validate, validate_or_raise


def _row(**kw: Any) -> dict[str, Any]:
    base = {
        "observation_id": "a",
        "product_id": "X",
        "year": 2020,
        "month": 1,
        "value": 10.0,
        "unit": "MAD/kg",
        "currency": "MAD",
        "confidence": "official",
        "precision": "exact",
        "collection_method": "api",
    }
    base.update(kw)
    return base


def test_clean_data_passes():
    assert validate([_row(), _row(observation_id="b")]).passed


def test_duplicate_ids_flagged():
    assert not validate([_row(), _row()]).passed


def test_nonpositive_price_flagged():
    assert not validate([_row(value=-5.0)]).passed


def test_negative_index_is_allowed():
    # inflation (percent) can legitimately be negative
    assert validate([_row(unit="percent", currency="index", value=-1.0)]).passed


def test_year_out_of_range_flagged():
    assert not validate([_row(year=1800)]).passed


def test_bad_unit_domain_flagged():
    assert not validate([_row(unit="MAD/barrel")]).passed


def test_validate_or_raise():
    with pytest.raises(QualityCheckFailed):
        validate_or_raise([_row(value=-1.0)])
