"""Avro serialization/deserialization for Kafka messages."""

import json
from pathlib import Path

import fastavro
from fastavro.schema import load_schema

SCHEMAS_DIR = Path(__file__).parent.parent.parent.parent / "config" / "kafka" / "schemas"

_schema_cache: dict[str, dict] = {}


def get_schema(name: str) -> dict:
    """Load and cache an Avro schema by name."""
    if name not in _schema_cache:
        path = SCHEMAS_DIR / f"{name}.avsc"
        with open(path) as f:
            _schema_cache[name] = json.load(f)
    return _schema_cache[name]


def serialize(record: dict, schema_name: str) -> bytes:
    """Serialize a dict to Avro bytes."""
    import io

    schema = get_schema(schema_name)
    buf = io.BytesIO()
    fastavro.schemaless_writer(buf, schema, record)
    return buf.getvalue()


def deserialize(data: bytes, schema_name: str) -> dict:
    """Deserialize Avro bytes to a dict."""
    import io

    schema = get_schema(schema_name)
    buf = io.BytesIO(data)
    return fastavro.schemaless_reader(buf, schema)
