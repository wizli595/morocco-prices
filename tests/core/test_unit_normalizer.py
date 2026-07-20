"""Tests for unit normalizer."""

import pytest

from src.core.models.errors import UnsupportedConversion
from src.core.transformers.unit_normalizer import (
    canonical_unit_for,
    is_index_unit,
    normalize_unit,
)


def test_tonne_to_kg():
    val, unit = normalize_unit(51250, "MAD/tonne", "MAD/kg")
    assert val == 51.25
    assert unit == "MAD/kg"


def test_same_unit_noop():
    val, _ = normalize_unit(90.0, "MAD/kg", "MAD/kg")
    assert val == 90.0


def test_unknown_conversion_raises():
    with pytest.raises(UnsupportedConversion):
        normalize_unit(100, "MAD/barrel", "MAD/kg")


def test_is_index_unit_true():
    assert is_index_unit("index_point") is True
    assert is_index_unit("percent") is True


def test_is_index_unit_false():
    assert is_index_unit("MAD/kg") is False


def test_canonical_unit_for_tonne():
    assert canonical_unit_for("MAD/tonne") == "MAD/kg"


def test_canonical_unit_for_unknown():
    assert canonical_unit_for("MAD/barrel") == "MAD/barrel"
