"""Kafka producer adapter for publishing observations."""

import structlog
from confluent_kafka import Producer

from src.adapters.kafka.avro_serde import serialize
from src.core.ports.publisher import BasePublisher
from src.core.models.observation import RawObservation

logger = structlog.get_logger()


class KafkaPublisher(BasePublisher):
    """Publishes Avro-serialized observations to Kafka."""

    def __init__(self, bootstrap_servers: str) -> None:
        self._producer = Producer({
            "bootstrap.servers": bootstrap_servers,
        })

    def publish(
        self,
        topic: str,
        observation: RawObservation,
    ) -> None:
        """Serialize and send one observation."""
        record = _observation_to_dict(observation)
        schema_name = f"raw_{observation.source_id.lower()}"
        value = serialize(record, schema_name)

        self._producer.produce(
            topic=topic,
            value=value,
            key=observation.observation_id.encode(),
        )

    def flush(self) -> None:
        """Wait for all pending messages to be delivered."""
        remaining = self._producer.flush(timeout=30)
        if remaining > 0:
            logger.warning("kafka.flush.incomplete", remaining=remaining)


def _observation_to_dict(obs: RawObservation) -> dict:
    """Convert observation to a flat dict for Avro."""
    return {
        "source_id": obs.source_id,
        "product_id": obs.product_id,
        "location_id": obs.location_id,
        "year": obs.year,
        "month": obs.month,
        "value": obs.value,
        "unit": obs.unit,
        "currency": obs.currency,
        "ingested_at": obs.collected_at.isoformat(),
        "pipeline_run_id": obs.raw_metadata.get("run_id", ""),
    }
