"""Tests for the plugin registry."""

from src.core.registry import get_collector, list_collectors


def test_collectors_registered():
    """All Phase 3 collectors should be registered."""
    # Importing the modules triggers @register_collector
    import src.collectors.faostat
    import src.collectors.manual
    import src.collectors.worldbank  # noqa: F401

    names = list_collectors()
    assert "worldbank" in names
    assert "faostat" in names
    assert "manual" in names


def test_get_collector_returns_class():
    """get_collector should return the class, not an instance."""
    import src.collectors.worldbank  # noqa: F401

    cls = get_collector("worldbank")
    assert isinstance(cls, type)


def test_get_collector_unknown_raises():
    """Should raise KeyError for unknown source."""
    import pytest

    with pytest.raises(KeyError, match="Unknown collector"):
        get_collector("nonexistent_source")
