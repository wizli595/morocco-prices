"""Numbeo scraper — current Morocco retail consumer prices (MAD/kg).

One page lists many products, so this exercises the BaseScraper contract's
one-page-to-many-observations path (unlike the one-page-per-product Selina
scraper).
"""

from src.collectors.base_scraper import BaseScraper, ScrapeTarget
from src.collectors.numbeo_parser import parse_food_table
from src.core.models.observation import RawObservation
from src.core.registry import register_collector

URL = "https://www.numbeo.com/food-prices/country_result.jsp?country=Morocco"


@register_collector("numbeo")
class NumbeoCollector(BaseScraper):
    """Scrape the Numbeo Morocco food-prices basket (crowd-sourced retail)."""

    @property
    def source_id(self) -> str:
        return "NUMBEO"

    @property
    def source_name(self) -> str:
        return "Numbeo"

    def targets(self) -> list[ScrapeTarget]:
        return [ScrapeTarget(URL)]

    def parse(self, html: str, target: ScrapeTarget) -> list[RawObservation]:
        return parse_food_table(html)
