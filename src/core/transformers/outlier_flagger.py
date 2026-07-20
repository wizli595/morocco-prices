"""Flag statistical outliers in price series."""

import statistics
from dataclasses import dataclass


@dataclass
class FlaggedPrice:
    """A price with an outlier flag."""

    observation_id: str
    value: float
    is_outlier: bool
    zscore: float


def _unflagged(values: list[tuple[str, float]]) -> list[FlaggedPrice]:
    """Return every value marked as a non-outlier (zscore 0)."""
    return [FlaggedPrice(obs_id, val, False, 0.0) for obs_id, val in values]


def flag_outliers(
    values: list[tuple[str, float]],
    threshold: float = 3.0,
) -> list[FlaggedPrice]:
    """Flag values where |z-score| exceeds threshold."""
    nums = [v for _, v in values]
    if len(nums) < 3:
        return _unflagged(values)

    mean = statistics.mean(nums)
    stdev = statistics.stdev(nums)
    if stdev == 0:
        return _unflagged(values)

    return [
        FlaggedPrice(obs_id, val, abs(z := (val - mean) / stdev) > threshold, z)
        for obs_id, val in values
    ]
