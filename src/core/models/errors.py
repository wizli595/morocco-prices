"""Custom exception hierarchy for MaPrix."""


class MaPrixError(Exception):
    """Base exception for all MaPrix errors."""


class CollectorError(MaPrixError):
    """Raised when a data collector fails."""


class SourceUnavailable(CollectorError):
    """Raised when an external source is unreachable."""

    def __init__(self, source: str, reason: str) -> None:
        self.source = source
        self.reason = reason
        super().__init__(f"{source}: {reason}")


class ParseError(CollectorError):
    """Raised when raw data cannot be parsed."""

    def __init__(self, source: str, detail: str) -> None:
        self.source = source
        self.detail = detail
        super().__init__(f"{source}: {detail}")


class SchemaViolation(MaPrixError):
    """Raised when data fails schema validation."""

    def __init__(self, field: str, expected: str, got: str) -> None:
        self.field = field
        super().__init__(f"{field}: expected {expected}, got {got}")


class UnsupportedConversion(MaPrixError):
    """Raised for unknown unit or currency conversion."""

    def __init__(self, from_val: str, to_val: str) -> None:
        super().__init__(f"No conversion: {from_val} → {to_val}")


class TransformError(MaPrixError):
    """Raised when a transformation step fails."""


class QualityCheckFailed(MaPrixError):
    """Raised when quality validation fails."""

    def __init__(self, failures: list[str]) -> None:
        self.failures = failures
        super().__init__(f"{len(failures)} checks failed")
