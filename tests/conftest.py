"""Shared test fixtures for MaPrix."""

from datetime import UTC, datetime

import pytest

from src.core.models.enums import (
    CollectionMethod,
    Confidence,
    Precision,
)
from src.core.models.observation import RawObservation


@pytest.fixture
def sample_observation() -> RawObservation:
    """A minimal valid observation for testing."""
    return RawObservation(
        source_id="TEST",
        product_id="MEAT-SHEEP",
        location_id="MA-NATIONAL",
        year=2024,
        month=6,
        day=None,
        value=90.2,
        value_min=None,
        value_max=None,
        unit="MAD/kg",
        currency="MAD",
        confidence=Confidence.OFFICIAL,
        precision=Precision.EXACT,
        collection_method=CollectionMethod.API,
        collected_at=datetime.now(tz=UTC),
        raw_metadata={"item_code": "977"},
    )
