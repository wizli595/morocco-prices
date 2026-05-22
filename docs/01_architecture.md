# Architecture Overview

## Project: Morocco Price Observatory (MaPrix)

A comprehensive, enterprise-grade data platform that collects, processes, and serves historical and current price data for Morocco - covering food, energy, housing, livestock, and services from the 1960s to present.

---

## High-Level Architecture

```
                    DATA SOURCES (10+)
                    │
        ┌───────────┼───────────────┬──────────────┬──────────────┐
        ▼           ▼               ▼              ▼              ▼
   World Bank    FAOSTAT         HCP Excel      WFP/HDX        News
   (REST API)   (Bulk CSV)     (XLS Download)   (CSV)        (Scraping)
        │           │               │              │              │
        ▼           ▼               ▼              ▼              ▼
   ┌────────────────────────────────────────────────────────────────┐
   │                    PYTHON COLLECTORS                           │
   │  worldbank.py  faostat.py  hcp.py  wfp.py  news.py manual.py │
   └───────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────────────┐
   │                    APACHE KAFKA                                │
   │                                                                │
   │  Confluent Schema Registry (Avro)                              │
   │                                                                │
   │  Topics:                                                       │
   │    raw.worldbank    raw.faostat    raw.hcp                     │
   │    raw.wfp          raw.news       raw.manual                  │
   │    processed.silver  alerts.quality  alerts.anomaly            │
   └───────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────────────┐
   │                    APACHE SPARK (PySpark)                      │
   │                                                                │
   │  ┌──────────┐    ┌──────────────┐    ┌───────────────┐        │
   │  │  BRONZE   │───►│    SILVER     │───►│     GOLD      │       │
   │  │          │    │              │    │               │        │
   │  │ Raw as   │    │ Cleaned      │    │ Star schema   │        │
   │  │ received │    │ Normalized   │    │ Enriched      │        │
   │  │ Per-src  │    │ Unified      │    │ Aggregated    │        │
   │  │ schema   │    │ Validated    │    │ Cross-checked │        │
   │  └──────────┘    └──────────────┘    └───────────────┘        │
   │                                                                │
   │  Jobs:                                                         │
   │    ingest_to_bronze.py      bronze_to_silver.py                │
   │    silver_to_gold.py        gold_to_warehouse.py               │
   │    quality_check.py         forecast.py                        │
   └───────────────────────────┬────────────────────────────────────┘
   │                           │
   │  DELTA LAKE               │
   │  (ACID on Parquet)        │
   │                           │
   │  bronze/                  │
   │  silver/                  │
   │  gold/                    │
   └───────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │    HIVE       │  │  POSTGRESQL  │  │ GREAT        │
   │  METASTORE    │  │  (Serving)   │  │ EXPECTATIONS │
   │               │  │              │  │              │
   │ Table catalog │  │ Star schema  │  │ Validation   │
   │ Partitions    │  │ Materialized │  │ Data docs    │
   │ Schema mgmt   │  │ For API/BI   │  │ Reports      │
   └──────────────┘  └──────┬───────┘  └──────────────┘
                            │
                   ┌────────┼────────┐
                   ▼                 ▼
            ┌────────────┐   ┌────────────┐
            │  FASTAPI   │   │  APACHE    │
            │            │   │  SUPERSET  │
            │ REST API   │   │            │
            │ Export     │   │ BI Dashb.  │
            │ endpoints  │   │ Charts     │
            └────────────┘   └────────────┘
                   │
   ┌───────────────┼───────────────┐
   ▼               ▼               ▼
GitHub          Kaggle         Data Dict
Release         Dataset        (auto-gen)
```

---

## Observability Stack

```
┌──────────────────────────────────────────────────────┐
│                    GRAFANA                            │
│                                                      │
│  ┌────────────────┐    ┌─────────────────────┐       │
│  │   METRICS       │    │      LOGS            │      │
│  │                │    │                     │       │
│  │  Prometheus    │    │  Loki               │       │
│  │  ◄── Kafka     │    │  ◄── Promtail       │       │
│  │  ◄── Spark     │    │      ◄── Docker     │       │
│  │  ◄── Postgres  │    │          stdout     │       │
│  │  ◄── App       │    │      ◄── Collectors │       │
│  └────────────────┘    │      ◄── Spark jobs │       │
│                        │      ◄── Airflow    │       │
│                        └─────────────────────┘       │
│                                                      │
│  Dashboards:                                         │
│    - Pipeline Health (jobs, latency, errors)         │
│    - Data Quality (coverage, freshness, anomalies)   │
│    - Infrastructure (CPU, mem, disk, Kafka lag)       │
│    - Collector Status (per-source success/fail)      │
└──────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. Medallion Architecture (Bronze / Silver / Gold)
- **Bronze**: Immutable raw data. Never modified after write. Source of truth for reprocessing.
- **Silver**: Cleaned, normalized to unified schema. Business rules applied. One schema across all sources.
- **Gold**: Star schema optimized for analytics. Pre-aggregated views. Cross-source reconciliation.

### 2. Schema-on-Write with Evolution
- Avro schemas in Kafka enforce structure at ingestion
- Delta Lake enforces schema at storage with evolution support
- Hive Metastore catalogs all tables with partition management

### 3. Idempotent Processing
- Every Spark job can be re-run safely (upsert, not insert)
- Delta Lake MERGE operations prevent duplicates
- Deterministic observation IDs (hash of natural keys)

### 4. Source Transparency
- Every price observation carries its source, confidence, and precision
- Cross-source conflicts are stored, not silently resolved
- Quality reports document coverage and gaps

### 5. Separation of Concerns
- Collectors only collect (no transformation)
- Spark only transforms (no collection)
- PostgreSQL only serves (no processing)
- Airflow only orchestrates (no business logic)

---

## Data Flow Summary

```
1. COLLECT  → Collector fetches from external source
2. PUBLISH  → Raw observation published to Kafka topic (Avro-serialized)
3. INGEST   → Spark Structured Streaming / batch reads Kafka → writes Bronze (Delta)
4. CLEAN    → Spark batch: Bronze → Silver (normalize, validate, deduplicate)
5. ENRICH   → Spark batch: Silver → Gold (star schema, aggregate, cross-validate)
6. LOAD     → Spark writes Gold → PostgreSQL (materialized star schema)
7. SERVE    → FastAPI reads PostgreSQL, Superset visualizes
8. PUBLISH  → Export Gold as CSV/Parquet to GitHub/Kaggle
9. VALIDATE → Great Expectations runs after each layer transition
10. MONITOR → Prometheus scrapes metrics, Loki aggregates logs, Grafana displays
```

---

## Key Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.12+ | All application code |
| Streaming | Apache Kafka | 3.7+ | Message bus between collectors and processing |
| Schema Mgmt | Confluent Schema Registry | 7.x | Avro schema enforcement |
| Processing | Apache Spark | 3.5+ | Batch + structured streaming ETL |
| Storage | Delta Lake | 3.x | ACID lakehouse on Parquet |
| Catalog | Hive Metastore | 3.x | Table/partition catalog |
| Warehouse | PostgreSQL | 16 | Serving layer for API/BI |
| Orchestration | Apache Airflow | 2.9+ | DAG scheduling, monitoring |
| API | FastAPI | 0.110+ | REST API for data access |
| BI | Apache Superset | 3.x | Dashboards, charts, exploration |
| Quality | Great Expectations | 0.18+ | Data validation framework |
| Metrics | Prometheus | 2.x | Time-series metrics collection |
| Logs | Grafana Loki | 2.x | Log aggregation |
| Log Shipper | Promtail | 2.x | Docker log collection |
| Dashboards | Grafana | 10.x | Unified metrics + logs UI |
| Containers | Docker + Compose | 24+ | Local deployment |
| CI/CD | GitHub Actions | - | Tests, builds, releases |

See [04_infrastructure.md](./04_infrastructure.md) for detailed service configuration.
