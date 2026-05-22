"""Port: contract for transformation steps."""

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class BaseTransformer(ABC):
    """A single transformation step in the pipeline."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Short name for logging and metrics."""

    @abstractmethod
    def transform(self, data: list[T]) -> list[T]:
        """Apply transformation, return modified data."""
