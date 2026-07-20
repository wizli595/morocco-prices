"""Parse FAOSTAT wide-format CSV rows into RawObservations."""

from datetime import UTC, datetime
from typing import Any

from src.core.models.enums import CollectionMethod, Confidence, Precision
from src.core.models.observation import RawObservation

MOROCCO_CODE = "143"

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

YEAR_RANGE = range(1991, 2026)


def is_morocco_row(row: dict[str, Any]) -> bool:
    """Check if a wide-format row is Morocco + tracked item."""
    return row.get("Area Code") == MOROCCO_CODE and row.get("Item Code") in ITEM_CODES


def parse_wide_row(row: dict[str, Any]) -> list[RawObservation]:
    """Unpivot one wide row into per-year observations."""
    item_code = row["Item Code"]
    element = row.get("Element", "")
    results: list[RawObservation] = []

    for year in YEAR_RANGE:
        val_str = row.get(f"Y{year}", "")
        if not val_str:
            continue
        flag = row.get(f"Y{year}F", "")
        results.append(_build_obs(row, item_code, element, year, val_str, flag))

    return results


def _build_obs(
    row: dict[str, Any],
    item_code: str,
    element: str,
    year: int,
    val_str: str,
    flag: str,
) -> RawObservation:
    return RawObservation(
        source_id="FAOSTAT",
        product_id=ITEM_CODES[item_code],
        location_id="MA-NATIONAL",
        year=year,
        month=None,
        day=None,
        value=float(val_str),
        value_min=None,
        value_max=None,
        unit=_detect_unit(element),
        currency=_detect_currency(element),
        confidence=_flag_to_confidence(flag),
        precision=Precision.EXACT,
        collection_method=CollectionMethod.FILE_DOWNLOAD,
        collected_at=datetime.now(tz=UTC),
        raw_metadata={"item_code": item_code, "element": element, "flag": flag},
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


def _flag_to_confidence(flag: str) -> Confidence:
    if flag == "A":
        return Confidence.OFFICIAL
    if flag == "E":
        return Confidence.ESTIMATED
    return Confidence.INSTITUTIONAL
