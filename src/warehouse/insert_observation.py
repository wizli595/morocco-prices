"""Insert a RawObservation into fact_prices."""

import structlog
from psycopg2.extensions import cursor as PgCursor

from src.core.models.observation import RawObservation
from src.warehouse.dimension_lookup import (
    get_location_key,
    get_product_key,
    get_source_key,
    get_time_key,
)

logger = structlog.get_logger()

INSERT_SQL = """
    INSERT INTO serving.fact_prices (
        observation_id, product_key, location_key,
        time_key, source_key,
        original_value, original_min, original_max,
        original_unit, original_currency,
        price_mad, confidence, precision,
        collection_method, pipeline_run_id
    ) VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s
    ) ON CONFLICT (observation_id) DO NOTHING
"""


def insert_observation(cur: PgCursor, obs: RawObservation, run_id: str) -> bool:
    """Insert one observation, return True if inserted."""
    product_key = get_product_key(cur, obs.product_id)
    location_key = get_location_key(cur, obs.location_id)
    source_key = get_source_key(cur, obs.source_id)
    time_key = get_time_key(obs.year, obs.month)

    if not product_key or not location_key or not source_key:
        logger.warning(
            "warehouse.observation.dropped",
            observation_id=obs.observation_id,
            source_id=obs.source_id,
            product_id=obs.product_id,
            location_id=obs.location_id,
            missing_product=not product_key,
            missing_location=not location_key,
            missing_source=not source_key,
        )
        return False

    cur.execute(
        INSERT_SQL,
        (
            obs.observation_id,
            product_key,
            location_key,
            time_key,
            source_key,
            obs.value,
            obs.value_min,
            obs.value_max,
            obs.unit,
            obs.currency,
            None,
            obs.confidence.value,
            obs.precision.value,
            obs.collection_method.value,
            run_id,
        ),
    )
    return True
