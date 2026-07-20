"""Run the quality rules and report or raise."""

from dataclasses import dataclass
from typing import Any

from src.core.models.errors import QualityCheckFailed
from src.core.quality import rules

_CHECKS = (
    rules.duplicate_ids,
    rules.nonpositive_prices,
    rules.year_out_of_range,
    rules.invalid_domains,
)


@dataclass(frozen=True)
class QualityReport:
    """Outcome of running all quality checks over a set of observations."""

    total: int
    failures: list[str]

    @property
    def passed(self) -> bool:
        return not self.failures


def validate(rows: list[dict[str, Any]]) -> QualityReport:
    """Run every rule and collect all failure messages."""
    failures: list[str] = []
    for check in _CHECKS:
        failures.extend(check(rows))
    return QualityReport(total=len(rows), failures=failures)


def validate_or_raise(rows: list[dict[str, Any]]) -> QualityReport:
    """Validate and raise QualityCheckFailed if any rule fails."""
    report = validate(rows)
    if not report.passed:
        raise QualityCheckFailed(report.failures)
    return report
