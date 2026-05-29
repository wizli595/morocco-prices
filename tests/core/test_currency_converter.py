"""Tests for currency converter."""

from src.core.transformers.currency_converter import (
    mad_to_usd,
    usd_to_mad,
)


def test_usd_to_mad_known_year():
    result = usd_to_mad(100.0, 2020)
    assert result is not None
    assert abs(result - 950.0) < 0.01


def test_mad_to_usd_known_year():
    result = mad_to_usd(950.0, 2020)
    assert result is not None
    assert abs(result - 100.0) < 0.01


def test_roundtrip_conversion():
    mad = usd_to_mad(50.0, 2015)
    usd = mad_to_usd(mad, 2015)
    assert abs(usd - 50.0) < 0.01


def test_unknown_year_returns_none():
    assert usd_to_mad(100.0, 1940) is None


def test_interpolated_year():
    """1976 is between 1975 and 1980, should interpolate."""
    result = usd_to_mad(100.0, 1976)
    assert result is not None
    assert 394.0 < result < 506.0
