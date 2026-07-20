"""Collector plugins. Importing this package registers every collector."""

from src.collectors import (  # noqa: F401
    faostat,
    faostat_cp,
    manual,
    numbeo,
    selina,
    worldbank,
)
