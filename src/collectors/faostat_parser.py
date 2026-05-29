"""Parse FAOSTAT bulk CSV rows into RawObservations."""

from datetime import datetime, timezone

from src.core.models.enums import CollectionMethod, Confidence, Precision
from src.core.models.observation import RawObservation

MOROCCO_CODE = "143"

# FAOSTAT item codes we care about
ITEM_CODES = {
    "977": "MEAT-SHEEP",
    "867": "MEAT-BEEF",
    "1017": "MEAT-GOAT",
    "1058": "MEAT-CHICKEN-BROILER",
    "882": "DAIRY-MILK-RAW",
    "15": "CEREAL-WHEAT-SOFT",
    "44": "CEREAL-BARLEY",
    "27": "CEREAL-RICE-ROUND",
}


def is_morocco_price_row(row: dict) -> bool:
    """Check if a CSV row is a Morocco producer price."""
    return (
        row.get("Area Code") == MOROCCO_CODE
        and row.get("Item Code") in ITEM_CODES
        and row.get("Value") not in (None, "")
    )


def parse_row(row: dict) -> RawObservation:
    """Convert one FAOSTAT CSV row to RawObservation."""
    item_code = row["Item Code"]
    element = row.get("Element", "")
    unit = _detect_unit(element)

    return RawObservation(
        source_id="FAOSTAT",
        product_id=ITEM_CODES[item_code],
        location_id="MA-NATIONAL",
        year=int(row["Year"]),
        month=None,
        day=None,
        value=float(row["Value"]),
        value_min=None,
        value_max=None,
        unit=unit,
        currency=_detect_currency(element),
        confidence=_detect_confidence(row.get("Flag", "")),
        precision=Precision.EXACT,
        collection_method=CollectionMethod.FILE_DOWNLOAD,
        collected_at=datetime.now(tz=timezone.utc),
        raw_metadata={
            "item_code": item_code,
            "element": element,
            "flag": row.get("Flag", ""),
        },
    )


def _detect_unit(element: str) -> str:
    if "USD/tonne" in element:
        return "USD/tonne"
    if "LCU/tonne" in element or "SLC" in element:
        return "MAD/tonne"
    return "index_point"


def _detect_currency(element: str) -> str:
    if "USD" in element:
        return "USD"
    if "LCU" in element or "SLC" in element:
        return "MAD"
    return "index"


def _detect_confidence(flag: str) -> Confidence:
    if flag == "A":
        return Confidence.OFFICIAL
    if flag == "E":
        return Confidence.ESTIMATED
    return Confidence.INSTITUTIONAL
