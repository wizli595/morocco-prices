"""Cleaned and normalized price record."""

from dataclasses import dataclass

from src.core.models.enums import (
    CollectionMethod,
    Confidence,
    Precision,
)


@dataclass(frozen=True)
class CleanPrice:
    """A price observation after normalization."""

    observation_id: str
    product_id: str
    location_id: str
    time_key: int
    source_id: str
    price_type_id: str

    # Original values (immutable, as reported)
    original_value: float | None
    original_min: float | None
    original_max: float | None
    original_unit: str
    original_currency: str

    # Normalized values
    price_mad: float | None
    price_usd: float | None
    price_real_mad: float | None
    price_min_mad: float | None
    price_max_mad: float | None

    # Quality metadata
    confidence: Confidence
    precision: Precision
    collection_method: CollectionMethod
    interpolation_method: str | None

    # Lineage
    pipeline_run_id: str

    @staticmethod
    def empty(observation_id: str, reason: str) -> "CleanPrice":
        """Create an empty record for skipped observations."""
        return CleanPrice(
            observation_id=observation_id,
            product_id="",
            location_id="",
            time_key=0,
            source_id="",
            price_type_id="",
            original_value=None,
            original_min=None,
            original_max=None,
            original_unit="",
            original_currency="",
            price_mad=None,
            price_usd=None,
            price_real_mad=None,
            price_min_mad=None,
            price_max_mad=None,
            confidence=Confidence.ANECDOTAL,
            precision=Precision.APPROXIMATE,
            collection_method=CollectionMethod.CALCULATED,
            interpolation_method=reason,
            pipeline_run_id="",
        )
