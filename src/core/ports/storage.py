"""Port: contract for storage backends."""

from abc import ABC, abstractmethod
from typing import Any


class BaseStorage(ABC):
    """Read/write interface for any storage backend."""

    @abstractmethod
    def read(self, path: str) -> list[dict[str, Any]]:
        """Read records from storage."""

    @abstractmethod
    def write(self, path: str, records: list[dict[str, Any]]) -> int:
        """Write records, return count written."""

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a path/table exists."""
