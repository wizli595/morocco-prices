"""Port: contract for all data collectors."""

from abc import ABC, abstractmethod
from datetime import datetime

from src.core.models.observation import RawObservation


class BaseCollector(ABC):
    """Every data source implements this contract."""

    @property
    @abstractmethod
    def source_id(self) -> str:
        """Unique identifier for this source."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name."""

    @abstractmethod
    def collect(self) -> list[RawObservation]:
        """Fetch observations from the external source."""

    @abstractmethod
    def check_freshness(self) -> datetime | None:
        """Return last-updated timestamp, or None if unknown."""
