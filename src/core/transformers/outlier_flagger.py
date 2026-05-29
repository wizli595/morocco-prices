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


def flag_outliers(
    values: list[tuple[str, float]],
    threshold: float = 3.0,
) -> list[FlaggedPrice]:
    """Flag values where |z-score| exceeds threshold."""
    if len(values) < 3:
        return [
            FlaggedPrice(obs_id, val, False, 0.0)
            for obs_id, val in values
        ]

    nums = [v for _, v in values]
    mean = statistics.mean(nums)
    stdev = statistics.stdev(nums)

    if stdev == 0:
        return [
            FlaggedPrice(obs_id, val, False, 0.0)
            for obs_id, val in values
        ]

    results: list[FlaggedPrice] = []
    for obs_id, val in values:
        z = (val - mean) / stdev
        results.append(FlaggedPrice(obs_id, val, abs(z) > threshold, z))

    return results
