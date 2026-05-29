"""Run all registered collectors and persist to PostgreSQL."""

import uuid
from datetime import datetime, timezone

import structlog

from scripts.db import get_connection
from src.collectors.manual import ManualCollector
from src.collectors.worldbank import WorldBankCollector
from src.warehouse.insert_observation import insert_observation

logger = structlog.get_logger()


def run_all() -> None:
    """Execute each collector and store observations."""
    run_id = f"run_{datetime.now(tz=timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    conn = get_connection()
    cur = conn.cursor()

    collectors = [ManualCollector(), WorldBankCollector()]

    total = 0
    for collector in collectors:
        name = collector.source_id
        logger.info("runner.collector.start", source=name)

        observations = collector.collect()
        inserted = 0
        for obs in observations:
            if insert_observation(cur, obs, run_id):
                inserted += 1

        conn.commit()
        total += inserted
        logger.info(
            "runner.collector.done",
            source=name,
            collected=len(observations),
            inserted=inserted,
        )

    cur.close()
    conn.close()
    logger.info("runner.complete", run_id=run_id, total_inserted=total)


if __name__ == "__main__":
    run_all()
