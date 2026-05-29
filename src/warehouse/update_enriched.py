"""Write enriched fields back to fact_prices."""

from psycopg2.extensions import cursor as PgCursor

UPDATE_SQL = """
    UPDATE serving.fact_prices
    SET price_mad = %s,
        price_usd = %s,
        price_real_mad = %s
    WHERE observation_id = %s
"""


def update_enriched_price(
    cur: PgCursor,
    observation_id: str,
    price_mad: float | None,
    price_usd: float | None,
    price_real_mad: float | None,
) -> None:
    """Update the normalized price columns for one observation."""
    cur.execute(UPDATE_SQL, (
        price_mad, price_usd, price_real_mad, observation_id,
    ))
