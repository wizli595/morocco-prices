"""Parse a Selina Wamucii product page into a price observation."""

import calendar
import re
from datetime import UTC, datetime

from selectolax.parser import HTMLParser

from src.core.models.enums import CollectionMethod, Confidence, Precision
from src.core.models.observation import RawObservation

PRICE_SELECTOR = ".swpc-price-value"
_PRICE_RE = re.compile(r"US\$\s?([0-9]+(?:\.[0-9]+)?)\s?/?\s?kg", re.IGNORECASE)
_DATE_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+(20\d{2})"
)
_MONTHS = {calendar.month_name[i]: i for i in range(1, 13)}


def parse_price(html: str, product_id: str) -> RawObservation | None:
    """Extract the USD/kg price and reference date from a Selina page."""
    tree = HTMLParser(html)
    node = tree.css_first(PRICE_SELECTOR)
    match = _PRICE_RE.search(node.text(strip=True)) if node else None
    if not match:
        return None
    year, month = _reference_date(tree)
    return RawObservation(
        source_id="SELINA",
        product_id=product_id,
        location_id="MA-NATIONAL",
        year=year,
        month=month,
        day=None,
        value=float(match.group(1)),
        value_min=None,
        value_max=None,
        unit="USD/kg",
        currency="USD",
        confidence=Confidence.ESTIMATED,
        precision=Precision.EXACT,
        collection_method=CollectionMethod.SCRAPE,
        collected_at=datetime.now(tz=UTC),
        raw_metadata={"source": "selinawamucii.com", "product_id": product_id},
    )


def _reference_date(tree: HTMLParser) -> tuple[int, int]:
    """Read the 'Month YYYY' the page reports, else fall back to today."""
    heading = tree.css_first("h1")
    match = _DATE_RE.search(heading.text(strip=True)) if heading else None
    if match:
        return int(match.group(2)), _MONTHS[match.group(1)]
    now = datetime.now(tz=UTC)
    return now.year, now.month
