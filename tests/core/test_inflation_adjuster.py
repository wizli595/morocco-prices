"""Tests for inflation adjuster."""

from src.core.transformers.inflation_adjuster import (
    adjust_to_real,
    inflation_rate,
    load_cpi_from_rows,
)


def _load_sample_cpi():
    """Load a small CPI series for testing."""
    load_cpi_from_rows([
        (2010, 100.0),
        (2015, 110.0),
        (2017, 115.0),
        (2020, 120.0),
    ])


def test_adjust_to_real_same_year():
    _load_sample_cpi()
    result = adjust_to_real(100.0, 2017)
    assert result is not None
    assert abs(result - 100.0) < 0.01


def test_adjust_to_real_older_year():
    """Prices were lower in 2010, so real value should be higher."""
    _load_sample_cpi()
    result = adjust_to_real(50.0, 2010)
    assert result is not None
    assert result > 50.0


def test_adjust_to_real_newer_year():
    """Prices higher in 2020, so real value should be lower."""
    _load_sample_cpi()
    result = adjust_to_real(50.0, 2020)
    assert result is not None
    assert result < 50.0


def test_adjust_missing_year_returns_none():
    _load_sample_cpi()
    assert adjust_to_real(50.0, 1960) is None


def test_inflation_rate():
    _load_sample_cpi()
    rate = inflation_rate(2010, 2020)
    assert rate is not None
    assert abs(rate - 0.20) < 0.01
