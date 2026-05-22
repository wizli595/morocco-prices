"""Dimension models for the star schema."""

from dataclasses import dataclass

from src.core.models.enums import LocationLevel, SourceReliability


@dataclass(frozen=True)
class Product:
    """A product in the price catalog."""

    product_id: str
    category: str
    subcategory: str
    product_name: str
    variety: str | None
    name_en: str
    name_fr: str
    name_ar: str | None
    canonical_unit: str
    is_subsidized: bool = False
    is_seasonal: bool = False


@dataclass(frozen=True)
class Location:
    """A geographic location in Morocco."""

    location_id: str
    country: str
    region: str | None
    province: str | None
    city: str | None
    market: str | None
    level: LocationLevel
    latitude: float | None = None
    longitude: float | None = None


@dataclass(frozen=True)
class Source:
    """A data source for price observations."""

    source_id: str
    source_name: str
    organization: str
    source_type: str
    reliability: SourceReliability
    url: str | None
    language: str
    update_frequency: str
    priority_rank: int
