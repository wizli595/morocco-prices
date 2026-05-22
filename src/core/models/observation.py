"""Core domain model: a single price observation."""

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

from src.core.models.enums import (
    CollectionMethod,
    Confidence,
    Precision,
)


@dataclass(frozen=True)
class RawObservation:
    """A price observation exactly as received from a source."""

    source_id: str
    product_id: str
    location_id: str
    year: int
    month: int | None
    day: int | None

    value: float | None
    value_min: float | None
    value_max: float | None
    unit: str
    currency: str

    confidence: Confidence
    precision: Precision
    collection_method: CollectionMethod

    collected_at: datetime
    raw_metadata: dict[str, str]

    @property
    def observation_id(self) -> str:
        """Deterministic ID from natural keys."""
        time_key = _build_time_key(self.year, self.month, self.day)
        raw = (
            f"{self.product_id}|{self.location_id}"
            f"|{time_key}|{self.source_id}|{self.unit}"
        )
        return sha256(raw.encode()).hexdigest()[:16]


def _build_time_key(year: int, month: int | None, day: int | None) -> int:
    """Encode year/month/day into YYYYMMDD integer."""
    m = month or 0
    d = day or 0
    return year * 10000 + m * 100 + d
