# Implementation Phases

## Overview

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
Project     Infra       Data Model   Collectors   Processing   Quality
Bootstrap   Setup       & Catalog    (Bronze)     (Silver/Gold)

    Phase 6 ──► Phase 7 ──► Phase 8 ──► Phase 9 ──► Phase 10
    Serving     Orchestr.   Observ-      Expand      Publishing
    (API/BI)    (Airflow)   ability      Sources     & Release
```

---

## Phase 0: Project Bootstrap

**Goal**: Repository setup, project structure, documentation, development environment.

### Tasks

- [ ] Initialize git repository
- [ ] Create project structure (all directories)
- [ ] Write `pyproject.toml` with all dependencies
- [ ] Write `Dockerfile` (Python 3.12 base with Spark, Delta Lake)
- [ ] Write `.env.example`
- [ ] Write `CLAUDE.md` (project conventions)
- [ ] Write `.gitignore` (data/, logs/, *.env, __pycache__, .venv/)
- [ ] Create virtual environment for local development
- [ ] Finalize all documentation in `docs/`
- [ ] Set up pre-commit hooks (ruff, mypy)

### Deliverables
- Clean repo with full directory structure
- All docs written and reviewed
- Local dev environment working

### Directory Structure
```
morocco-prices/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── update.yml
│       └── publish.yml
├── config/
│   ├── airflow/
│   │   └── dags/
│   ├── grafana/
│   │   ├── provisioning/
│   │   │   ├── datasources/
│   │   │   └── dashboards/
│   │   └── dashboards/
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── promtail/
│   │   └── promtail-config.yml
│   ├── superset/
│   │   └── superset_config.py
│   └── kafka/
│       └── schemas/           # Avro schemas
│           ├── raw_worldbank.avsc
│           ├── raw_faostat.avsc
│           ├── raw_hcp.avsc
│           ├── raw_wfp.avsc
│           ├── raw_news.avsc
│           └── raw_manual.avsc
├── data/
│   ├── bronze/                # Raw data (gitignored)
│   ├── silver/                # Cleaned data (gitignored)
│   ├── gold/                  # Final dataset (committed)
│   ├── warehouse/             # Hive warehouse dir (gitignored)
│   ├── checkpoints/           # Spark checkpoints (gitignored)
│   ├── manual/                # Hand-entered historical data (committed)
│   │   └── historical_anchors.csv
│   └── seeds/                 # Dimension seed data (committed)
│       ├── products.csv
│       ├── locations.csv
│       └── sources.csv
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── observation.py     # Core domain models
│   │   ├── dimensions.py      # Dimension dataclasses
│   │   └── enums.py           # Enumerations
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── base.py            # AbstractCollector
│   │   ├── worldbank.py
│   │   ├── faostat.py
│   │   ├── hcp.py
│   │   ├── wfp.py
│   │   ├── news.py
│   │   ├── selina.py
│   │   └── manual.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── producer.py        # Kafka producer (collector → topic)
│   │   ├── consumer.py        # Kafka consumer (topic → bronze)
│   │   └── schemas.py         # Avro schema loader
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── bronze_writer.py   # Kafka → Delta Lake bronze
│   │   ├── bronze_to_silver.py
│   │   ├── silver_to_gold.py
│   │   ├── gold_to_warehouse.py
│   │   ├── transformers/
│   │   │   ├── __init__.py
│   │   │   ├── normalizer.py      # Unit/currency normalization
│   │   │   ├── parser.py          # Price range parsing
│   │   │   ├── currency.py        # Historical FX conversion
│   │   │   ├── inflation.py       # CPI-based real price adjustment
│   │   │   ├── interpolator.py    # Gap filling
│   │   │   ├── deduplicator.py    # Cross-source dedup
│   │   │   └── outlier.py         # Anomaly detection
│   │   └── reconciler.py         # Cross-source conflict resolution
│   ├── quality/
│   │   ├── __init__.py
│   │   ├── expectations.py    # Great Expectations suite definitions
│   │   ├── validator.py       # Run validations per layer
│   │   └── reporter.py        # Generate quality reports
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── time_series.py     # Decomposition, trend analysis
│   │   ├── forecaster.py      # Price forecasting
│   │   └── cross_source.py    # Source agreement scoring
│   ├── warehouse/
│   │   ├── __init__.py
│   │   ├── connection.py      # PostgreSQL connection factory
│   │   ├── schema.sql         # DDL for serving tables
│   │   └── loader.py          # Gold → PostgreSQL materialization
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app factory
│   │   ├── dependencies.py    # DB sessions, config
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── prices.py      # GET /api/prices
│   │   │   ├── products.py    # GET /api/products
│   │   │   ├── trends.py      # GET /api/trends
│   │   │   ├── sources.py     # GET /api/sources
│   │   │   ├── quality.py     # GET /api/quality
│   │   │   └── export.py      # GET /api/export (CSV/Parquet/JSON)
│   │   └── templates/         # Jinja2 (if adding HTML views later)
│   ├── publishing/
│   │   ├── __init__.py
│   │   ├── github_release.py
│   │   ├── kaggle_push.py
│   │   └── data_dictionary.py
│   ├── logging/
│   │   ├── __init__.py
│   │   └── setup.py           # structlog JSON logging config
│   └── config.py              # Settings (pydantic-settings)
├── tests/
│   ├── conftest.py
│   ├── test_collectors/
│   ├── test_processing/
│   ├── test_quality/
│   ├── test_analysis/
│   ├── test_api/
│   └── test_integration/
├── notebooks/
│   ├── 01_exploration.ipynb
│   └── 02_validation.ipynb
├── docs/
│   ├── 01_architecture.md
│   ├── 02_data_model.md
│   ├── 03_product_catalog.md
│   ├── 04_infrastructure.md
│   ├── 05_phases.md
│   ├── 06_logging.md
│   └── sources/
│       ├── sources.md
│       └── sheep_prices_morocco.md
├── scripts/
│   ├── init_postgres.sql      # Create databases, extensions
│   ├── init_kafka_topics.sh   # Create all Kafka topics
│   └── init_delta_tables.py   # Create Delta Lake tables
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.spark           # Spark + Delta + Hive image
├── pyproject.toml
├── .env.example
├── .gitignore
├── CLAUDE.md
└── README.md
```

---

## Phase 1: Infrastructure Setup

**Goal**: All Docker services running and communicating.

### Tasks

- [ ] Write `docker-compose.yml` with all 17 services
- [ ] Write `Dockerfile` for Python app (collectors, API)
- [ ] Write `Dockerfile.spark` (Spark + Delta Lake + Hive jars)
- [ ] Write `scripts/init_postgres.sql` (create all 4 databases)
- [ ] Write `scripts/init_kafka_topics.sh` (create all topics)
- [ ] Configure Hive Metastore to use PostgreSQL backend
- [ ] Configure Spark to use Hive Metastore + Delta Lake
- [ ] Write `config/prometheus/prometheus.yml`
- [ ] Write `config/promtail/promtail-config.yml`
- [ ] Provision Grafana datasources (Prometheus + Loki)
- [ ] Write basic Grafana dashboard (infrastructure health)
- [ ] Verify: `docker compose up` starts all services cleanly
- [ ] Verify: Kafka topics accessible from Spark
- [ ] Verify: Spark reads/writes Delta Lake tables via Hive
- [ ] Verify: Logs flow from containers → Promtail → Loki → Grafana
- [ ] Verify: Prometheus scrapes all targets

### Acceptance Criteria
- `docker compose up` → all 17 services healthy (green)
- Spark UI shows worker registered
- Grafana shows infrastructure dashboard
- Kafka topics exist and are writable

---

## Phase 2: Data Model & Catalog

**Goal**: Star schema defined in Hive, dimension tables seeded, Avro schemas registered.

### Tasks

- [ ] Write Avro schemas for all 6 Kafka raw topics
- [ ] Register Avro schemas in Schema Registry
- [ ] Write `data/seeds/products.csv` (full product catalog ~500 rows)
- [ ] Write `data/seeds/locations.csv` (Morocco hierarchy ~200 rows)
- [ ] Write `data/seeds/sources.csv` (~20 rows)
- [ ] Write `scripts/init_delta_tables.py`:
  - Create bronze Delta tables (per source)
  - Create silver Delta table (unified)
  - Create gold Delta tables (fact + dimensions + aggregations)
- [ ] Register all tables in Hive Metastore
- [ ] Write `src/warehouse/schema.sql` (PostgreSQL serving layer DDL)
- [ ] Seed dimension tables from CSV
- [ ] Generate dim_time (1960-2030, daily grain with Moroccan calendar events)
- [ ] Write `src/models/observation.py` (core domain models)
- [ ] Write `src/models/dimensions.py` (dimension dataclasses)
- [ ] Write `src/models/enums.py` (Category, Confidence, Precision, etc.)
- [ ] Verify: `spark.sql("SHOW TABLES")` lists all tables
- [ ] Verify: Dimension tables have correct row counts

### Acceptance Criteria
- All Avro schemas registered and versioned
- Hive Metastore has all table definitions
- Dimensions seeded (products, locations, time, sources)
- PostgreSQL serving schema created
- Domain models with type safety

---

## Phase 3: Collectors (Bronze Layer)

**Goal**: First 3 collectors running, data landing in Kafka and Bronze Delta Lake.

### Priority Order (start with richest + easiest)

| Priority | Collector | Source Type | Why First |
|----------|----------|-------------|-----------|
| 1 | World Bank | REST API | Easiest, free, no auth, 1960-2024 |
| 2 | FAOSTAT | Bulk CSV | Richest, 1991-2024, producer prices |
| 3 | Manual | CSV file | Historical anchors (1970, 1985 data) |
| 4 | HCP | Excel download | Regional CPI, 18 cities |
| 5 | WFP | CSV from HDX | Market-level food prices |
| 6 | News | Web scraping | Eid prices, most complex |
| 7 | Selina | Web scraping | Export/import prices |

### Tasks

- [ ] Write `src/collectors/base.py` (AbstractCollector)
  - `collect() → list[RawObservation]`
  - `get_source_metadata() → SourceMetadata`
  - `check_freshness() → datetime`
  - Retry logic, rate limiting, error handling
- [ ] Write `src/ingestion/producer.py` (Kafka Avro producer)
- [ ] Write `src/ingestion/schemas.py` (Avro schema loader)
- [ ] Write `src/processing/bronze_writer.py` (Kafka consumer → Delta Lake)
- [ ] Write `src/logging/setup.py` (structlog JSON config)
- [ ] Implement `src/collectors/worldbank.py`
  - Fetch CPI, inflation for Morocco (1960-present)
  - Publish to `raw.worldbank` topic
  - Write tests
- [ ] Implement `src/collectors/faostat.py`
  - Download bulk CSV, filter Morocco + relevant items
  - Parse all food/livestock producer prices
  - Publish to `raw.faostat` topic
  - Write tests
- [ ] Implement `src/collectors/manual.py`
  - Read `data/manual/historical_anchors.csv`
  - Publish to `raw.manual` topic
  - Write tests
- [ ] Write `data/manual/historical_anchors.csv` with all known historical data points
- [ ] Verify: Bronze Delta tables contain data after running collectors
- [ ] Verify: Kafka topics have messages with correct Avro schema
- [ ] Verify: Logs appear in Grafana/Loki

### Acceptance Criteria
- 3 collectors working end-to-end
- Bronze tables populated with raw data
- Kafka messages properly serialized (Avro)
- Structured JSON logs flowing to Loki
- Unit tests passing

---

## Phase 4: Processing (Silver & Gold)

**Goal**: Spark jobs transform Bronze → Silver → Gold. Star schema populated.

### Tasks

- [ ] Write `src/processing/transformers/normalizer.py`
  - Unit normalization (tonne→kg, quintal→kg, etc.)
  - Currency detection and standardization
- [ ] Write `src/processing/transformers/parser.py`
  - Parse "entre 3000 et 7000" → min=3000, max=7000
  - Handle French and Arabic number formats
- [ ] Write `src/processing/transformers/currency.py`
  - Historical MAD/USD exchange rate lookup
  - Populate `ref_exchange_rates` from World Bank
- [ ] Write `src/processing/transformers/inflation.py`
  - CPI-based real price calculation (base 2017)
  - Populate `ref_cpi_index` from World Bank CPI
- [ ] Write `src/processing/transformers/interpolator.py`
  - Index anchoring: price = anchor * (index / anchor_index)
  - Linear interpolation between known points
  - Flag all interpolated values
- [ ] Write `src/processing/transformers/deduplicator.py`
  - Deterministic observation_id prevents exact dupes
  - Near-duplicate detection (same product/time/location, different sources)
- [ ] Write `src/processing/transformers/outlier.py`
  - IQR-based outlier detection per product time series
  - Z-score flagging
  - Don't remove, just flag
- [ ] Write `src/processing/reconciler.py`
  - When multiple sources disagree, apply priority ranking
  - Store all versions, mark "preferred" source
- [ ] Write `src/processing/bronze_to_silver.py` (Spark job)
  - Read all bronze tables
  - Apply all transformers
  - Write to silver Delta table (unified schema)
- [ ] Write `src/processing/silver_to_gold.py` (Spark job)
  - Populate fact_prices from silver
  - Generate surrogate keys (join with dimensions)
  - Compute pre-aggregated views
  - Write to gold Delta tables
- [ ] Write `src/processing/gold_to_warehouse.py` (Spark job)
  - Materialize gold tables → PostgreSQL serving layer
- [ ] Write tests for each transformer (with chispa for Spark DataFrames)

### Acceptance Criteria
- Silver table has unified, normalized observations
- Gold star schema fully populated
- PostgreSQL serving layer has queryable data
- All transformations tested
- Interpolated values clearly flagged
- Outliers detected but not removed

---

## Phase 5: Data Quality

**Goal**: Great Expectations validates every layer. Quality reports generated.

### Tasks

- [ ] Install and configure Great Expectations
- [ ] Write Bronze expectations:
  - No null primary fields per source schema
  - Values within expected ranges
  - Date fields parseable
  - Source-specific validations
- [ ] Write Silver expectations:
  - `observation_id` unique
  - `price_mad` > 0 (where not null)
  - `price_min_mad` <= `price_max_mad`
  - `confidence` in valid set
  - `year` between 1960 and current year
  - No orphaned foreign keys
- [ ] Write Gold expectations:
  - Star schema referential integrity
  - Aggregation consistency (SUM checks)
  - Coverage thresholds (>80% of expected product-year combos)
- [ ] Write cross-source expectations:
  - FAOSTAT and HCP prices within 15% for overlapping items/years
  - CPI trend direction matches inflation rate direction
- [ ] Write `src/quality/validator.py` (run expectations, collect results)
- [ ] Write `src/quality/reporter.py` (generate JSON + HTML quality reports)
- [ ] Generate coverage matrix (products × years × regions × data availability)
- [ ] Store validation results in Delta Lake for historical tracking
- [ ] Create Superset/Grafana dashboard for quality metrics

### Acceptance Criteria
- Expectations defined for all 3 layers
- Validation runs automatically after each layer transition
- Quality reports generated (HTML + JSON)
- Coverage matrix shows data gaps visually
- Quality metrics visible in Grafana

---

## Phase 6: Serving Layer (API + BI)

**Goal**: FastAPI REST API + Superset dashboards live and queryable.

### Tasks

- [ ] Write `src/api/main.py` (FastAPI app factory)
- [ ] Write `src/api/dependencies.py` (DB pool, config injection)
- [ ] Write API routes:
  - `GET /api/prices` - Filter by product, location, year, source. Paginated.
  - `GET /api/prices/{product_id}/timeseries` - Time series for a product
  - `GET /api/products` - Product catalog (tree structure)
  - `GET /api/products/{product_id}` - Product detail + available data summary
  - `GET /api/locations` - Location hierarchy
  - `GET /api/sources` - Source metadata + freshness
  - `GET /api/trends` - Price trends (aggregated)
  - `GET /api/quality` - Latest quality report
  - `GET /api/quality/coverage` - Coverage matrix
  - `GET /api/export` - Download full dataset (CSV, Parquet, JSON)
  - `GET /api/export/{product_id}` - Download single product data
  - `GET /health` - Health check
  - `GET /metrics` - Prometheus metrics endpoint
- [ ] Add request validation (pydantic models for query params)
- [ ] Add response caching (Redis or in-memory)
- [ ] Write OpenAPI documentation (auto-generated by FastAPI)
- [ ] Configure Superset:
  - Connect to PostgreSQL serving database
  - Create datasets (fact_prices joined with dimensions)
  - Build dashboards:
    - **Price Explorer**: Filter by product, see time series chart
    - **Regional Comparison**: Same product across cities
    - **Source Coverage**: What data we have, from where
    - **Eid Al Adha Tracker**: Sheep prices over the years
    - **Inflation Impact**: Real vs nominal prices
    - **Data Quality**: Freshness, gaps, anomalies
- [ ] Write API tests

### Acceptance Criteria
- All API endpoints working with correct responses
- Superset dashboards built and queryable
- API documentation accessible at `/docs`
- Export endpoints produce valid CSV/Parquet

---

## Phase 7: Orchestration (Airflow)

**Goal**: Full pipeline automated with Airflow DAGs.

### Tasks

- [ ] Write DAG: `collect_worldbank` (monthly)
  - Run collector → Kafka → Bronze
- [ ] Write DAG: `collect_faostat` (monthly)
- [ ] Write DAG: `collect_hcp` (monthly, when new data published)
- [ ] Write DAG: `collect_wfp` (monthly)
- [ ] Write DAG: `collect_news` (weekly, Eid-season: daily)
- [ ] Write DAG: `bronze_to_silver` (after any collector completes)
- [ ] Write DAG: `silver_to_gold` (after silver updated)
- [ ] Write DAG: `gold_to_warehouse` (after gold updated)
- [ ] Write DAG: `quality_check` (after each layer transition)
- [ ] Write DAG: `full_pipeline` (manual trigger: end-to-end)
- [ ] Write DAG: `publish_dataset` (manual trigger: export + push)
- [ ] Configure alerting:
  - Email/Slack on DAG failure
  - SLA monitoring (collector should complete within 30 min)
- [ ] Write sensor: Check if source has new data before collecting

### DAG Dependency Graph

```
collect_worldbank ──┐
collect_faostat  ──┤
collect_hcp      ──┼──► bronze_to_silver ──► quality_check_silver
collect_wfp      ──┤                              │
collect_news     ──┤                              ▼
collect_manual   ──┘                    silver_to_gold ──► quality_check_gold
                                              │
                                              ▼
                                    gold_to_warehouse
                                              │
                                              ▼
                                    refresh_superset_cache
```

### Acceptance Criteria
- All DAGs registered and visible in Airflow UI
- Full pipeline runs end-to-end via manual trigger
- Individual collectors schedulable independently
- Quality checks integrated into pipeline
- Alerting configured

---

## Phase 8: Observability

**Goal**: Full monitoring, logging, and alerting operational.

### Tasks

- [ ] Finalize `src/logging/setup.py`:
  - structlog with JSON output
  - Correlation IDs across pipeline stages
  - Log levels: DEBUG (dev), INFO (prod), WARNING, ERROR
- [ ] Add structured logging to all collectors:
  - `collector.start`, `collector.fetch`, `collector.publish`, `collector.complete`
  - Include: source, records_count, duration_ms, errors
- [ ] Add structured logging to all Spark jobs:
  - `spark.job.start`, `spark.job.complete`, `spark.transform.*`
  - Include: input_rows, output_rows, duration_ms, errors
- [ ] Add Prometheus metrics:
  - `maprix_collector_runs_total` (counter, labels: source, status)
  - `maprix_collector_records_total` (counter, labels: source)
  - `maprix_collector_duration_seconds` (histogram, labels: source)
  - `maprix_spark_job_duration_seconds` (histogram, labels: job_name)
  - `maprix_observations_total` (gauge, labels: layer, category)
  - `maprix_quality_score` (gauge, labels: layer)
  - `maprix_api_requests_total` (counter, labels: endpoint, status)
  - `maprix_api_latency_seconds` (histogram, labels: endpoint)
- [ ] Build Grafana dashboards:
  - **Pipeline Health**: Job success/fail rates, durations, throughput
  - **Data Quality**: Coverage %, freshness, anomaly counts
  - **Collector Status**: Per-source last run, next run, record counts
  - **Infrastructure**: Container CPU/mem, Kafka lag, Postgres connections
  - **API**: Request rate, latency percentiles, error rate
- [ ] Configure Grafana alerts:
  - Collector failed 2+ times → alert
  - Kafka consumer lag > 1000 → alert
  - Quality score dropped below threshold → alert
  - API error rate > 5% → alert
- [ ] Write Loki log queries for common troubleshooting

### Acceptance Criteria
- All services producing structured JSON logs
- Prometheus metrics from all components
- 5+ Grafana dashboards operational
- Alerts configured and tested
- Correlation IDs trace a record from collection to serving

---

## Phase 9: Expand Sources

**Goal**: All 7 collectors operational. Full data coverage.

### Tasks

- [ ] Implement `src/collectors/hcp.py`
  - Download Excel files from HCP website
  - Parse CPI by 18 cities, by division
  - Handle base year changes (2006, 2017)
  - Write tests
- [ ] Implement `src/collectors/wfp.py`
  - Download CSV from HDX
  - Filter Morocco records
  - Map commodities to product catalog
  - Write tests
- [ ] Implement `src/collectors/news.py`
  - Scrape Medias24, Hespress, Le360 for price articles
  - NLP: Extract prices, items, cities from article text
  - Handle French and Arabic
  - Write tests
- [ ] Implement `src/collectors/selina.py`
  - Scrape Selina Wamucii export/import prices
  - Map to product catalog
  - Write tests
- [ ] Expand `data/manual/historical_anchors.csv`:
  - All data points from FAO "Small Ruminants" report (1960-1986)
  - All data points from INRA sheep report (1970-1998)
  - Any data extractable from Bank Al-Maghrib annual reports
- [ ] Re-run full pipeline with all sources
- [ ] Validate cross-source agreement
- [ ] Update coverage matrix
- [ ] Fix any data quality issues surfaced

### Acceptance Criteria
- 7 collectors all operational
- Coverage matrix shows significant improvement
- Cross-source validation passing
- No regression in existing data

---

## Phase 10: Publishing & Release

**Goal**: Dataset published to GitHub and Kaggle. Documentation complete.

### Tasks

- [ ] Write `src/publishing/data_dictionary.py`
  - Auto-generate from Hive Metastore + dimension tables
  - Include: field descriptions, value ranges, coverage stats
  - Output: JSON + Markdown
- [ ] Write `src/publishing/github_release.py`
  - Package gold layer as CSV + Parquet
  - Create GitHub Release with artifacts
  - Include data dictionary, quality report, coverage matrix
- [ ] Write `src/publishing/kaggle_push.py`
  - Use Kaggle API to create/update dataset
  - Include metadata (description, tags, license)
- [ ] Write comprehensive README.md:
  - Project description and motivation
  - Dataset description and schema
  - How to use the data
  - How to run the pipeline
  - Architecture overview with diagram
  - Contributing guide
  - License (CC-BY-4.0 for data, MIT for code)
- [ ] Write `.github/workflows/ci.yml` (tests + lint on PR)
- [ ] Write `.github/workflows/update.yml` (monthly pipeline run)
- [ ] Write `.github/workflows/publish.yml` (release dataset)
- [ ] Create initial dataset release (v0.1.0)
- [ ] Submit to Kaggle
- [ ] Share on relevant communities (r/datasets, r/morocco, Hacker News)

### Acceptance Criteria
- Dataset published on GitHub Releases
- Dataset published on Kaggle
- README is comprehensive and polished
- CI/CD pipeline green
- Data dictionary auto-generated
- License clear

---

## Phase Dependency Matrix

```
Phase  | Depends On     | Can Parallelize With
-------|----------------|---------------------
0      | None           | -
1      | 0              | -
2      | 1              | -
3      | 2              | -
4      | 3              | -
5      | 4              | 6 (API can start)
6      | 4              | 5 (Quality)
7      | 3, 4, 6        | 8 (Observability)
8      | 1              | 7 (Orchestration), 5 (Quality)
9      | 3, 4           | 6, 7, 8
10     | 5, 6, 7, 9     | -
```

### Parallelization Opportunities

- **Phase 5 + Phase 6**: Quality and Serving are independent
- **Phase 7 + Phase 8**: Orchestration and Observability are independent
- **Phase 9**: Can start as soon as Phase 3 pattern is established (each new collector follows same pattern)

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| HCP changes Excel format | Bronze collector breaks | Schema validation in collector, alert on failure |
| FAOSTAT API down (observed 521 during research) | No fresh data | Fallback to bulk download, cache last good data |
| News sites block scraper | Missing Eid prices | Rotate User-Agent, add delays, manual fallback |
| Spark OOM on large FAOSTAT file | Processing fails | Increase worker memory, partition data |
| Hive Metastore schema evolution | Downstream breaks | BACKWARD compatibility in Schema Registry |
| Data quality issues not caught | Bad data in gold layer | Great Expectations on every layer transition |
| Docker Compose too heavy for dev machine | Slow development | Profiles: `core` for dev, `full` for testing |
