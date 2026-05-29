"""Run all transformers on existing data and enrich fact_prices."""

import structlog

from scripts.db import get_connection
from src.core.transformers.currency_converter import mad_to_usd, usd_to_mad
from src.core.transformers.inflation_adjuster import adjust_to_real, load_cpi_from_rows
from src.core.transformers.unit_normalizer import is_index_unit, normalize_unit
from src.warehouse.read_prices import fetch_all_prices, fetch_cpi_series
from src.warehouse.update_enriched import update_enriched_price

logger = structlog.get_logger()


def run() -> None:
    """Enrich all observations with normalized prices."""
    conn = get_connection()
    cur = conn.cursor()

    cpi_rows = fetch_cpi_series(cur)
    load_cpi_from_rows(cpi_rows)
    logger.info("processing.cpi_loaded", years=len(cpi_rows))

    prices = fetch_all_prices(cur)
    enriched = 0

    for row in prices:
        mad, usd, real = _enrich_row(row)
        update_enriched_price(
            cur, row["observation_id"], mad, usd, real,
        )
        enriched += 1

    conn.commit()
    cur.close()
    conn.close()
    logger.info("processing.complete", enriched=enriched)


def _enrich_row(row: dict) -> tuple[float | None, float | None, float | None]:
    """Compute price_mad, price_usd, price_real_mad for one row."""
    value = row["original_value"]
    unit = row["original_unit"]
    currency = row["original_currency"]
    year = row["year"]

    if value is None or is_index_unit(unit):
        return None, None, None

    price_mad = _to_mad(value, unit, currency, year)
    price_usd = mad_to_usd(price_mad, year) if price_mad else None
    price_real = adjust_to_real(price_mad, year) if price_mad else None

    return price_mad, price_usd, price_real


def _to_mad(
    value: float, unit: str, currency: str, year: int,
) -> float | None:
    """Convert any value to MAD in canonical unit."""
    if currency == "MAD" or currency == "index":
        normalized, _ = normalize_unit(value, unit, "MAD/kg")
        return normalized
    if currency == "USD":
        usd_val, _ = normalize_unit(value, unit, "USD/kg")
        return usd_to_mad(usd_val, year)
    return None


if __name__ == "__main__":
    run()
