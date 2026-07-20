"""Pure data-quality rules over price observations (no I/O)."""

from typing import Any

from src.core.models.enums import CollectionMethod, Confidence, Precision

INDEX_UNITS = {"index_point", "percent"}
ALLOWED_UNITS = {"MAD/kg", "MAD/tonne", "USD/tonne", "index_point", "percent"}
ALLOWED_CURRENCIES = {"MAD", "USD", "index"}
CONFIDENCES = {c.value for c in Confidence}
PRECISIONS = {p.value for p in Precision}
METHODS = {m.value for m in CollectionMethod}

Rows = list[dict[str, Any]]


def duplicate_ids(rows: Rows) -> list[str]:
    """Observation ids must be unique."""
    seen: set[str] = set()
    dups: set[str] = set()
    for r in rows:
        oid = r["observation_id"]
        (dups if oid in seen else seen).add(oid)
    return [f"duplicate observation_id: {d}" for d in sorted(dups)]


def nonpositive_prices(rows: Rows) -> list[str]:
    """Actual prices (non-index rows) must be strictly positive."""
    return [
        f"non-positive price: {r['observation_id']} = {r['value']}"
        for r in rows
        if r["unit"] not in INDEX_UNITS
        and r.get("value") is not None
        and r["value"] <= 0
    ]


def year_out_of_range(rows: Rows, lo: int = 1960, hi: int = 2026) -> list[str]:
    """Years must fall within the supported range."""
    return [
        f"year out of range: {r['observation_id']} = {r['year']}"
        for r in rows
        if r["year"] < lo or r["year"] > hi
    ]


def _domain(rows: Rows, field: str, allowed: set[str]) -> list[str]:
    bad = {r[field] for r in rows if r.get(field) is not None} - allowed
    return [f"unexpected {field}: {v}" for v in sorted(bad)]


def invalid_domains(rows: Rows) -> list[str]:
    """Enum-like fields must stay within their allowed value sets."""
    return (
        _domain(rows, "unit", ALLOWED_UNITS)
        + _domain(rows, "currency", ALLOWED_CURRENCIES)
        + _domain(rows, "confidence", CONFIDENCES)
        + _domain(rows, "precision", PRECISIONS)
        + _domain(rows, "collection_method", METHODS)
    )
