"""Run all registered collectors and persist to PostgreSQL."""

from datetime import UTC, datetime

import psycopg2
import structlog
from psycopg2.extensions import cursor as PgCursor

import src.collectors  # noqa: F401  # registers every collector plugin
from scripts.db import get_connection
from src.core.models.errors import MaPrixError
from src.core.models.observation import RawObservation
from src.core.ports.collector import BaseCollector
from src.core.registry import get_collector, list_collectors
from src.warehouse.insert_observation import insert_observation

logger = structlog.get_logger()


def run_all() -> None:
    """Execute each registered collector and store its observations."""
    run_id = f"run_{datetime.now(tz=UTC).strftime('%Y%m%d_%H%M%S')}"
    conn = get_connection()
    cur = conn.cursor()

    total = 0
    for collector in _all_collectors():
        total += _run_collector(cur, collector, run_id)
        conn.commit()

    cur.close()
    conn.close()
    logger.info("runner.complete", run_id=run_id, total_inserted=total)


def _all_collectors() -> list[BaseCollector]:
    """Instantiate every collector known to the plugin registry."""
    return [get_collector(source_id)() for source_id in list_collectors()]


def _run_collector(cur: PgCursor, collector: BaseCollector, run_id: str) -> int:
    """Collect from one source and persist each observation."""
    name = collector.source_id
    logger.info("runner.collector.start", source=name)

    try:
        observations = collector.collect()
    except MaPrixError as exc:
        logger.warning("runner.collector.error", source=name, error=str(exc))
        return 0

    inserted = sum(_persist(cur, obs, run_id) for obs in observations)

    logger.info(
        "runner.collector.done",
        source=name,
        collected=len(observations),
        inserted=inserted,
    )
    return inserted


def _persist(cur: PgCursor, obs: RawObservation, run_id: str) -> int:
    """Insert one observation inside a savepoint so failures stay isolated."""
    cur.execute("SAVEPOINT obs_sp")
    try:
        inserted = insert_observation(cur, obs, run_id)
    except psycopg2.Error:
        cur.execute("ROLLBACK TO SAVEPOINT obs_sp")
        logger.warning(
            "runner.observation.error",
            observation_id=obs.observation_id,
            source=obs.source_id,
        )
        return 0
    cur.execute("RELEASE SAVEPOINT obs_sp")
    return 1 if inserted else 0


if __name__ == "__main__":
    run_all()
