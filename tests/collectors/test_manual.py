"""Tests for the Manual collector."""

from src.collectors.manual import ManualCollector
from src.core.models.enums import Confidence, CollectionMethod


def test_manual_collects_historical_anchors():
    """Should read all rows from historical_anchors.csv."""
    collector = ManualCollector()
    observations = collector.collect()

    assert len(observations) >= 4
    assert all(o.source_id == "MANUAL" for o in observations)


def test_manual_sheep_1970():
    """Should find the 1970 sheep meat price."""
    collector = ManualCollector()
    observations = collector.collect()

    sheep_1970 = [
        o for o in observations
        if o.product_id == "MEAT-SHEEP" and o.year == 1970
    ]
    assert len(sheep_1970) >= 1
    assert sheep_1970[0].value == 7.80
    assert sheep_1970[0].unit == "MAD/kg"


def test_manual_confidence_is_academic():
    """Manual entries should have academic confidence."""
    collector = ManualCollector()
    observations = collector.collect()

    for obs in observations:
        assert obs.confidence == Confidence.ESTIMATED
        assert obs.collection_method == CollectionMethod.MANUAL


def test_manual_source_metadata_present():
    """Each observation should carry source document info."""
    collector = ManualCollector()
    observations = collector.collect()

    for obs in observations:
        assert "source_document" in obs.raw_metadata
