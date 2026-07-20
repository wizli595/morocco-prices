"""Template-method base class for web-scraping collectors.

The crawl loop lives here once; concrete scrapers implement only
``targets()`` (which pages) and ``parse()`` (how to read one).
"""

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
    """One page to scrape and the product it describes."""

    url: str
    product_id: str


class BaseScraper(BaseCollector):
    """Collector that scrapes a fixed list of pages, one observation each."""

    @abstractmethod
    def targets(self) -> list[ScrapeTarget]:
        """Return the pages this scraper should visit."""

    @abstractmethod
    def parse(self, html: str, target: ScrapeTarget) -> RawObservation | None:
        """Turn one page's HTML into an observation, or None if absent."""

    def collect(self) -> list[RawObservation]:
        """Crawl every target politely and collect the parsed observations."""
        targets = self.targets()
        found = [obs for t in targets if (obs := self._scrape(t))]
        logger.info(
            "scraper.complete",
            source=self.source_id,
            records=len(found),
            attempted=len(targets),
        )
        return found

    def _scrape(self, target: ScrapeTarget) -> RawObservation | None:
        try:
            html = fetch_html(target.url, source=self.source_id)
        except SourceUnavailable as exc:
            logger.warning("scraper.target.skip", url=target.url, error=str(exc))
            return None
        return self.parse(html, target)

    def check_freshness(self) -> None:
        return None
