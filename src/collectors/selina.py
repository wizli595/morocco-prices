"""Selina Wamucii scraper — current Morocco commodity prices (USD/kg)."""

from src.collectors.base_scraper import BaseScraper, ScrapeTarget
from src.collectors.selina_parser import parse_price
from src.core.models.observation import RawObservation
from src.core.registry import register_collector

BASE = "https://www.selinawamucii.com/insights/prices/morocco/"

# Selina URL slug -> internal product_id (only products present in dim_product)
PRODUCTS = {
    "beef": "MEAT-BEEF",
    "mutton": "MEAT-SHEEP",
    "chicken-meat": "MEAT-CHICKEN-BROILER",
    "goat-meat": "MEAT-GOAT",
    "sardines": "FISH-SARDINE-FRESH",
}


@register_collector("selina")
class SelinaCollector(BaseScraper):
    """Scrape current Morocco commodity prices from Selina Wamucii."""

    @property
    def source_id(self) -> str:
        return "SELINA"

    @property
    def source_name(self) -> str:
        return "Selina Wamucii"

    def targets(self) -> list[ScrapeTarget]:
        return [
            ScrapeTarget(f"{BASE}{slug}/", product_id)
            for slug, product_id in PRODUCTS.items()
        ]

    def parse(self, html: str, target: ScrapeTarget) -> RawObservation | None:
        return parse_price(html, target.product_id)
