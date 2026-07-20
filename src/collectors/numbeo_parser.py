"""Parse the Numbeo Morocco food-prices table into observations."""

import re
from datetime import UTC, datetime

from selectolax.parser import HTMLParser

from src.core.models.enums import CollectionMethod, Confidence, Precision
from src.core.models.observation import RawObservation

ITEM_MAP = {  # item-name substring -> product_id (per-kg retail items only)
    "Beef Round": "MEAT-BEEF",
    "Chicken Fillets": "MEAT-CHICKEN-BROILER",
    "White Rice": "CEREAL-RICE-ROUND",
    "Apples": "FRUIT-APPLE",
    "Tomato": "VEG-TOMATO",
    "Potato": "VEG-POTATO",
    "Onion": "VEG-ONION",
}
_PRICE_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)")


def parse_food_table(html: str) -> list[RawObservation]:
    """Extract every mapped per-kg retail price from the Numbeo page."""
    tree = HTMLParser(html)
    now = datetime.now(tz=UTC)
    out: list[RawObservation] = []
    for row in tree.css("table.data_wide_table tr"):
        cells = row.css("td")
        if len(cells) < 2:
            continue
        obs = _row_to_obs(cells[0].text(strip=True), cells[1].text(strip=True), now)
        if obs:
            out.append(obs)
    return out


def _row_to_obs(name: str, price_text: str, now: datetime) -> RawObservation | None:
    product_id = next((pid for k, pid in ITEM_MAP.items() if k in name), None)
    price = _PRICE_RE.search(price_text)
    if not product_id or not price:
        return None
    return RawObservation(
        source_id="NUMBEO",
        product_id=product_id,
        location_id="MA-NATIONAL",
        year=now.year,
        month=now.month,
        day=None,
        value=float(price.group(1)),
        value_min=None,
        value_max=None,
        unit="MAD/kg",
        currency="MAD",
        confidence=Confidence.ANECDOTAL,
        precision=Precision.APPROXIMATE,
        collection_method=CollectionMethod.SCRAPE,
        collected_at=now,
        raw_metadata={"source": "numbeo.com", "item": name},
    )
