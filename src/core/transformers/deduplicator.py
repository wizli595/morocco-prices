"""Deduplicate observations across sources."""

from dataclasses import dataclass


@dataclass
class PriceRow:
    """Lightweight row for dedup comparison."""

    observation_id: str
    product_id: str
    location_id: str
    time_key: int
    source_id: str
    value: float | None
    priority: int


def deduplicate(rows: list[PriceRow]) -> list[PriceRow]:
    """Keep highest-priority source per product/location/time."""
    best: dict[str, PriceRow] = {}

    for row in rows:
        key = _natural_key(row)
        existing = best.get(key)
        if existing is None or row.priority < existing.priority:
            best[key] = row

    return list(best.values())


def _natural_key(row: PriceRow) -> str:
    """Build grouping key for deduplication."""
    return f"{row.product_id}|{row.location_id}|{row.time_key}"
