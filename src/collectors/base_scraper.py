"""Template base for scrapers: the crawl loop, written once."""

from abc import abstractmethod
from dataclasses import dataclass

import structlog

from src.adapters.http.scraper import fetch_html
from src.core.models.errors import SourceUnavailable
from src.core.models.observation import RawObservation
from src.core.ports.collector import BaseCollector

logger = structlog.get_logger()


@dataclass(frozen=True)
class ScrapeTarget:
    """One page to scrape; ``product_id`` is set when a page is one product."""

    url: str
    product_id: str = ""


class BaseScraper(BaseCollector):
    """Collector that scrapes a fixed list of pages into observations."""

    @abstractmethod
    def targets(self) -> list[ScrapeTarget]:
        """Return the pages this scraper should visit."""

    @abstractmethod
    def parse(self, html: str, target: ScrapeTarget) -> list[RawObservation]:
        """Turn one page's HTML into zero or more observations."""

    def collect(self) -> list[RawObservation]:
        """Crawl every target politely and collect the parsed observations."""
        targets = self.targets()
        found: list[RawObservation] = []
        for target in targets:
            found.extend(self._scrape(target))
        logger.info(
            "scraper.complete",
            source=self.source_id,
            records=len(found),
            pages=len(targets),
        )
        return found

    def _scrape(self, target: ScrapeTarget) -> list[RawObservation]:
        try:
            html = fetch_html(target.url, source=self.source_id)
        except SourceUnavailable as exc:
            logger.warning("scraper.target.skip", url=target.url, error=str(exc))
            return []
        return self.parse(html, target)

    def check_freshness(self) -> None:
        return None
