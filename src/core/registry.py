"""Plugin registry with decorator-based auto-registration."""

from typing import TypeVar

from src.core.ports.collector import BaseCollector

T = TypeVar("T")

_COLLECTOR_REGISTRY: dict[str, type[BaseCollector]] = {}


def register_collector(source_id: str):
    """Decorator to register a collector class by source_id."""

    def decorator(cls: type[BaseCollector]) -> type[BaseCollector]:
        if source_id in _COLLECTOR_REGISTRY:
            raise ValueError(f"Duplicate collector: {source_id}")
        _COLLECTOR_REGISTRY[source_id] = cls
        return cls

    return decorator


def get_collector(source_id: str) -> type[BaseCollector]:
    """Retrieve a registered collector class by source_id."""
    cls = _COLLECTOR_REGISTRY.get(source_id)
    if cls is None:
        available = ", ".join(sorted(_COLLECTOR_REGISTRY))
        raise KeyError(f"Unknown collector '{source_id}'. Available: {available}")
    return cls


def list_collectors() -> list[str]:
    """Return all registered collector source_ids."""
    return sorted(_COLLECTOR_REGISTRY.keys())
