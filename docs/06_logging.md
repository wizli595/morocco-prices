# Logging & Observability Strategy

## Overview

Three pillars of observability, unified in Grafana:

```
┌──────────────────────────────────────────────────────────┐
│                       GRAFANA                            │
│                                                          │
│   ┌────────────┐   ┌────────────┐   ┌────────────┐      │
│   │  METRICS   │   │    LOGS    │   │   TRACES   │      │
│   │            │   │            │   │  (future)  │      │
│   │ Prometheus │   │   Loki     │   │            │      │
│   └────────────┘   └────────────┘   └────────────┘      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 1. Structured Logging

### Library: structlog

All Python code uses `structlog` for structured JSON logging. Every log line is machine-parseable.

### Log Format

```json
{
  "timestamp": "2026-05-22T14:30:00.123Z",
  "level": "info",
  "event": "collector.fetch.complete",
  "logger": "src.collectors.faostat",
  "service": "collector",
  "run_id": "run_20260522_143000",
  "correlation_id": "abc123-def456",
  "source": "FAOSTAT",
  "records_fetched": 1247,
  "duration_ms": 3421,
  "status": "success"
}
```

### Log Fields (Standard)

Every log line MUST include:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | When the event occurred |
| `level` | string | debug, info, warning, error, critical |
| `event` | string | Dot-notation event name (see naming below) |
| `logger` | string | Module path |
| `service` | string | Service name (collector, processor, api, etc.) |
| `run_id` | string | Pipeline run identifier |
| `correlation_id` | string | Traces a record from collection to serving |

### Event Naming Convention

Dot-notation: `{component}.{action}.{status}`

```
collector.start                    # Collector begins
collector.fetch.start              # HTTP request initiated
collector.fetch.complete           # HTTP response received
collector.fetch.error              # HTTP request failed
collector.parse.start              # Parsing response
collector.parse.complete           # Parsing done
collector.publish.start            # Publishing to Kafka
collector.publish.complete         # Published to Kafka
collector.complete                 # Collector finished

spark.job.start                    # Spark job submitted
spark.job.stage.start              # Spark stage begins
spark.job.stage.complete           # Spark stage done
spark.transform.normalize          # Unit normalization step
spark.transform.currency           # Currency conversion step
spark.transform.dedup              # Deduplication step
spark.transform.outlier            # Outlier detection step
spark.job.complete                 # Spark job finished
spark.job.error                    # Spark job failed

quality.validation.start           # GE validation begins
quality.validation.complete        # GE validation done
quality.expectation.fail           # Single expectation failed
quality.report.generated           # Quality report written

api.request.start                  # API request received
api.request.complete               # API response sent
api.request.error                  # API error

kafka.produce.success              # Message published
kafka.produce.error                # Publish failed
kafka.consume.success              # Message consumed
kafka.consume.error                # Consume failed

airflow.dag.start                  # DAG triggered
airflow.dag.complete               # DAG finished
airflow.dag.fail                   # DAG failed
airflow.task.start                 # Task started
airflow.task.complete              # Task completed
```

### Context-Specific Fields

**Collectors:**
```json
{
  "source": "FAOSTAT",
  "url": "https://bulks-faostat.fao.org/...",
  "records_fetched": 1247,
  "records_published": 1247,
  "records_skipped": 3,
  "skip_reason": "missing_required_field",
  "duration_ms": 3421,
  "http_status": 200,
  "response_size_bytes": 1048576
}
```

**Spark Jobs:**
```json
{
  "job_name": "bronze_to_silver",
  "input_table": "bronze_faostat",
  "output_table": "silver_prices",
  "input_rows": 50000,
  "output_rows": 48750,
  "rows_deduplicated": 1250,
  "rows_flagged_outlier": 23,
  "duration_ms": 12500,
  "spark_app_id": "app-20260522143000-0001"
}
```

**API Requests:**
```json
{
  "method": "GET",
  "path": "/api/prices",
  "query_params": {"product_id": "MEAT-SHEEP", "year_from": 2020},
  "status_code": 200,
  "response_rows": 48,
  "duration_ms": 85,
  "client_ip": "127.0.0.1"
}
```

**Quality Checks:**
```json
{
  "layer": "silver",
  "suite": "silver_prices_expectations",
  "expectations_total": 15,
  "expectations_passed": 14,
  "expectations_failed": 1,
  "failed_expectations": ["expect_column_values_to_be_between:price_mad"],
  "success_rate": 0.933,
  "evaluated_rows": 48750
}
```

---

## 2. Log Levels

| Level | When to Use | Example |
|-------|------------|---------|
| **DEBUG** | Detailed diagnostic info. Dev only. | "Parsing row 1247 from FAOSTAT CSV" |
| **INFO** | Normal operations. Things that should happen. | "Collector FAOSTAT completed: 1247 records" |
| **WARNING** | Unexpected but handled. Non-critical. | "FAOSTAT API returned 429, retrying in 5s" |
| **ERROR** | Operation failed. Needs attention. | "Failed to parse HCP Excel: unexpected format" |
| **CRITICAL** | System-level failure. Immediate attention. | "PostgreSQL connection refused" |

### Level Configuration

| Environment | Default Level | Verbose Components |
|-------------|-------------|-------------------|
| Development | DEBUG | All |
| Testing | INFO | Quality checks at DEBUG |
| Production | INFO | Collectors at INFO, Spark at WARNING |

---

## 3. Correlation ID Flow

A single correlation ID traces a data record from collection to serving:

```
Collector generates ID
        │
        ▼
┌─ correlation_id: "abc123" ─────────────────────────────┐
│                                                         │
│  1. Collector logs: collector.fetch.complete             │
│  2. Kafka message header: X-Correlation-ID: abc123      │
│  3. Bronze writer logs: bronze.write.complete            │
│  4. Silver processor logs: silver.transform.complete     │
│  5. Gold builder logs: gold.build.complete               │
│  6. Warehouse loader logs: warehouse.load.complete       │
│  7. API request log: api.request.complete                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**
```python
import uuid
import structlog

# Generate at collection time
correlation_id = str(uuid.uuid4())[:12]

# Bind to logger context
log = structlog.get_logger().bind(
    correlation_id=correlation_id,
    run_id=run_id,
    source="FAOSTAT"
)

# Pass through Kafka message headers
headers = [("X-Correlation-ID", correlation_id.encode())]
producer.produce(topic, value=message, headers=headers)

# Consumer extracts and re-binds
correlation_id = dict(msg.headers()).get("X-Correlation-ID").decode()
log = structlog.get_logger().bind(correlation_id=correlation_id)
```

---

## 4. Log Collection Pipeline

```
Python App (structlog)
    │
    ▼ writes to stdout (JSON)
    │
Docker captures stdout
    │
    ▼ /var/lib/docker/containers/{id}/{id}-json.log
    │
Promtail reads Docker logs
    │
    ▼ Adds labels: container_name, service, compose_project
    │
    ▼ Parses JSON structured fields
    │
Loki stores and indexes
    │
    ▼ Indexed labels: service, level, event, source
    │
Grafana queries via LogQL
```

### Promtail Configuration

```yaml
# config/promtail/promtail-config.yml

server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
        filters:
          - name: label
            values: ["com.docker.compose.project=maprix"]
    relabel_configs:
      # Extract container name as label
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'
      # Extract service name from compose label
      - source_labels: ['__meta_docker_container_label_com_docker_compose_service']
        target_label: 'service'
    pipeline_stages:
      # Parse Docker JSON log wrapper
      - docker: {}
      # Parse structlog JSON inside log message
      - json:
          expressions:
            level: level
            event: event
            source: source
            run_id: run_id
            correlation_id: correlation_id
            duration_ms: duration_ms
      # Set log level as label
      - labels:
          level:
          event:
          source:
```

---

## 5. Metrics (Prometheus)

### Custom Application Metrics

```python
# Exposed via /metrics endpoint (prometheus_client)

from prometheus_client import Counter, Histogram, Gauge

# Collector metrics
collector_runs = Counter(
    'maprix_collector_runs_total',
    'Total collector runs',
    ['source', 'status']  # status: success, error
)

collector_records = Counter(
    'maprix_collector_records_total',
    'Total records collected',
    ['source']
)

collector_duration = Histogram(
    'maprix_collector_duration_seconds',
    'Collector execution time',
    ['source'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]
)

# Processing metrics
spark_job_duration = Histogram(
    'maprix_spark_job_duration_seconds',
    'Spark job execution time',
    ['job_name'],
    buckets=[10, 30, 60, 120, 300, 600, 1800]
)

observations_total = Gauge(
    'maprix_observations_total',
    'Total observations in layer',
    ['layer', 'category']
)

# Quality metrics
quality_score = Gauge(
    'maprix_quality_score',
    'Quality validation success rate',
    ['layer']
)

quality_expectations_failed = Counter(
    'maprix_quality_expectations_failed_total',
    'Failed quality expectations',
    ['layer', 'expectation']
)

# API metrics
api_requests = Counter(
    'maprix_api_requests_total',
    'API requests',
    ['endpoint', 'method', 'status']
)

api_latency = Histogram(
    'maprix_api_latency_seconds',
    'API response latency',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)
```

### Infrastructure Metrics (Auto-Scraped)

| Target | Exporter | Metrics |
|--------|---------|---------|
| Kafka | JMX exporter (built into Confluent image) | Message rate, consumer lag, partition count |
| PostgreSQL | `postgres-exporter` | Connections, query duration, table sizes |
| Spark | Spark metrics servlet | Job duration, stage failures, executor memory |
| Docker | cAdvisor (optional) | Container CPU, memory, network |

### Prometheus Configuration

```yaml
# config/prometheus/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'

  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka:9101']  # JMX exporter

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'spark'
    static_configs:
      - targets: ['spark-master:4040']
    metrics_path: '/metrics/json'

  - job_name: 'airflow'
    static_configs:
      - targets: ['airflow-webserver:8082']
    metrics_path: '/admin/metrics'
```

---

## 6. Grafana Dashboards

### Dashboard 1: Pipeline Health

| Panel | Type | Query |
|-------|------|-------|
| Pipeline runs (24h) | Stat | `sum(maprix_collector_runs_total)` |
| Success rate | Gauge | `sum(rate(maprix_collector_runs_total{status="success"}[24h])) / sum(rate(maprix_collector_runs_total[24h]))` |
| Collector duration | Heatmap | `maprix_collector_duration_seconds_bucket` |
| Records collected | Time series | `rate(maprix_collector_records_total[1h])` |
| Recent errors | Log panel | `{service=~"collector.*"} |= "error"` |
| Spark job status | Table | `maprix_spark_job_duration_seconds` |

### Dashboard 2: Data Quality

| Panel | Type | Query |
|-------|------|-------|
| Quality score by layer | Gauge | `maprix_quality_score` |
| Failed expectations | Table | `maprix_quality_expectations_failed_total` |
| Observations by layer | Bar | `maprix_observations_total` |
| Coverage % | Stat | Custom query on PostgreSQL |
| Recent quality logs | Log panel | `{event=~"quality.*"}` |

### Dashboard 3: Infrastructure

| Panel | Type | Query |
|-------|------|-------|
| Kafka consumer lag | Time series | `kafka_consumer_group_lag` |
| PostgreSQL connections | Gauge | `pg_stat_activity_count` |
| Container memory | Time series | Per container |
| Disk usage | Gauge | Delta Lake directory sizes |
| Spark worker status | Stat | Active executors |

### Dashboard 4: API Performance

| Panel | Type | Query |
|-------|------|-------|
| Request rate | Time series | `rate(maprix_api_requests_total[5m])` |
| P50/P95/P99 latency | Time series | `histogram_quantile(0.95, maprix_api_latency_seconds_bucket)` |
| Error rate | Gauge | `rate(maprix_api_requests_total{status=~"5.."}[5m])` |
| Top endpoints | Table | `topk(10, sum by (endpoint)(rate(maprix_api_requests_total[1h])))` |

---

## 7. Alerting Rules

### Grafana Alert Rules

```yaml
# Critical
- alert: CollectorFailedRepeatedly
  expr: sum(increase(maprix_collector_runs_total{status="error"}[1h])) > 2
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Collector {{ $labels.source }} failed 2+ times in 1 hour"

- alert: PostgresDown
  expr: pg_up == 0
  for: 1m
  labels:
    severity: critical

# Warning
- alert: KafkaConsumerLagHigh
  expr: kafka_consumer_group_lag > 1000
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Kafka consumer lag > 1000 for {{ $labels.topic }}"

- alert: QualityScoreDrop
  expr: maprix_quality_score < 0.9
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Quality score dropped below 90% for {{ $labels.layer }}"

- alert: SparkJobSlow
  expr: maprix_spark_job_duration_seconds > 1800
  for: 0m
  labels:
    severity: warning
  annotations:
    summary: "Spark job {{ $labels.job_name }} took > 30 minutes"

- alert: APIHighLatency
  expr: histogram_quantile(0.95, rate(maprix_api_latency_seconds_bucket[5m])) > 2
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "API P95 latency > 2 seconds"

- alert: APIHighErrorRate
  expr: rate(maprix_api_requests_total{status=~"5.."}[5m]) / rate(maprix_api_requests_total[5m]) > 0.05
  for: 5m
  labels:
    severity: warning
```

---

## 8. Log Retention

| Component | Retention | Reason |
|-----------|----------|--------|
| Loki (all logs) | 7 days | Troubleshooting window |
| Prometheus metrics | 15 days | Trend analysis |
| Quality reports (GE) | Permanent | Historical quality tracking |
| Pipeline run metadata | Permanent | Audit trail |
| Airflow logs | 30 days | DAG debugging |

---

## 9. Useful LogQL Queries

```logql
# All errors in the last hour
{service=~".+"} |= "error" | json | level="error"

# Collector FAOSTAT logs
{service="collector"} | json | source="FAOSTAT"

# Trace a specific run
{service=~".+"} | json | run_id="run_20260522_143000"

# Trace a specific record through the pipeline
{service=~".+"} | json | correlation_id="abc123"

# Slow collectors (>60s)
{service="collector"} | json | event="collector.complete" | duration_ms > 60000

# Quality failures
{service=~".+"} | json | event="quality.expectation.fail"

# API errors with details
{service="api"} | json | status_code >= 500
```
