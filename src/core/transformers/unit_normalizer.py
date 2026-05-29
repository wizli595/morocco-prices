"""Normalize units to canonical form (MAD/kg, MAD/L, etc.)."""

CONVERSION_FACTORS: dict[tuple[str, str], float] = {
    ("MAD/tonne", "MAD/kg"): 0.001,
    ("USD/tonne", "USD/kg"): 0.001,
    ("MAD/quintal", "MAD/kg"): 0.01,
    ("MAD/100kg", "MAD/kg"): 0.01,
    ("DH/kg", "MAD/kg"): 1.0,
    ("DH/tonne", "MAD/kg"): 0.001,
}


def normalize_unit(
    value: float,
    from_unit: str,
    to_unit: str,
) -> tuple[float, str]:
    """Convert value between units, return (new_value, new_unit)."""
    if from_unit == to_unit:
        return value, to_unit

    key = (from_unit, to_unit)
    factor = CONVERSION_FACTORS.get(key)
    if factor is None:
        return value, from_unit

    return value * factor, to_unit


def is_index_unit(unit: str) -> bool:
    """Check if this unit is a price index, not an actual price."""
    return unit in ("index_point", "percent")


def canonical_unit_for(unit: str) -> str:
    """Find the canonical target unit for a given source unit."""
    for (from_u, to_u) in CONVERSION_FACTORS:
        if from_u == unit:
            return to_u
    return unit
