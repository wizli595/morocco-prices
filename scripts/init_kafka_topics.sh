#!/bin/bash
# Create all Kafka topics for MaPrix

KAFKA_BROKER="${KAFKA_BOOTSTRAP_SERVERS:-kafka:9092}"

wait_for_kafka() {
    echo "Waiting for Kafka to be ready..."
    while ! kafka-topics --bootstrap-server "$KAFKA_BROKER" --list >/dev/null 2>&1; do
        sleep 2
    done
    echo "Kafka is ready."
}

create_topic() {
    local name=$1
    local partitions=$2
    local retention_ms=$3

    kafka-topics --bootstrap-server "$KAFKA_BROKER" \
        --create --if-not-exists \
        --topic "$name" \
        --partitions "$partitions" \
        --config retention.ms="$retention_ms"

    echo "Created topic: $name (partitions=$partitions)"
}

wait_for_kafka

# Raw collector topics (7 days retention)
SEVEN_DAYS=604800000
create_topic "raw.worldbank"  1 "$SEVEN_DAYS"
create_topic "raw.faostat"    3 "$SEVEN_DAYS"
create_topic "raw.hcp"        1 "$SEVEN_DAYS"
create_topic "raw.wfp"        1 "$SEVEN_DAYS"
create_topic "raw.news"       1 "$SEVEN_DAYS"
create_topic "raw.manual"     1 "$SEVEN_DAYS"

# Processing topics (3 days retention)
THREE_DAYS=259200000
create_topic "processed.silver" 3 "$THREE_DAYS"

# Alert topics (30 days retention)
THIRTY_DAYS=2592000000
create_topic "alerts.quality"  1 "$THIRTY_DAYS"
create_topic "alerts.anomaly"  1 "$THIRTY_DAYS"

echo "All topics created."
