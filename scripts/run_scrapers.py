"""Run only the web-scraping collectors and persist to PostgreSQL.

Scrapers refresh current retail/market prices on a faster cadence than the
bulk sources, so they run in their own Airflow DAG rather than the monthly
full pipeline.
"""

from datetime import UTC, datetime

import structlog

import src.collectors  # noqa: F401  # registers every collector plugin
from scripts.db import get_connection
from scripts.run_collectors import _run_collector
from src.collectors.base_scraper import BaseScraper
from src.core.registry import get_collector, list_collectors

logger = structlog.get_logger()


def run() -> None:
    """Execute every registered scraper collector and store its prices."""
    run_id = f"scrape_{datetime.now(tz=UTC).strftime('%Y%m%d_%H%M%S')}"
    conn = get_connection()
    cur = conn.cursor()

    total = 0
    for source_id in list_collectors():
        collector = get_collector(source_id)
        if issubclass(collector, BaseScraper):
            total += _run_collector(cur, collector(), run_id)
            conn.commit()

    cur.close()
    conn.close()
    logger.info("scrapers.complete", run_id=run_id, total_inserted=total)


if __name__ == "__main__":
    run()
