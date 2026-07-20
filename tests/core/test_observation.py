"""Tests for the RawObservation model."""

from src.core.models.observation import _build_time_key


def test_build_time_key_annual():
    """Year only should produce YYYY0000."""
    assert _build_time_key(2024, None, None) == 20240000


def test_build_time_key_monthly():
    """Year + month should produce YYYYMM00."""
    assert _build_time_key(2024, 6, None) == 20240600


def test_build_time_key_daily():
    """Full date should produce YYYYMMDD."""
    assert _build_time_key(2024, 6, 15) == 20240615


def test_observation_id_deterministic(sample_observation):
    """Same inputs should produce same ID."""
    id1 = sample_observation.observation_id
    id2 = sample_observation.observation_id
    assert id1 == id2
    assert len(id1) == 16


def test_observation_id_differs_by_year(sample_observation):
    """Different year should produce different ID."""
    from dataclasses import replace

    other = replace(sample_observation, year=2023)
    assert sample_observation.observation_id != other.observation_id


def test_observation_is_frozen(sample_observation):
    """Should not allow attribute mutation."""
    import pytest

    with pytest.raises(AttributeError):
        sample_observation.year = 2025  # type: ignore[misc]
