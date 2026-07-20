# MaPrix — Morocco Price Observatory

![CI](https://github.com/wizli595/morocco-prices/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Code](https://img.shields.io/badge/license-MIT-green)
![Data](https://img.shields.io/badge/data-CC--BY--4.0-orange)

An enterprise-grade data platform that collects, processes, and serves historical and current price data for Morocco — from a loaf of *khobz* to a head of sheep.

## Why This Exists

No unified dataset exists for Moroccan prices. Data is scattered across 30+ sources in 3 languages — behind APIs, in Excel files, in PDFs, in news articles. This project unifies it all into a single, queryable, versioned dataset.

## What's Inside

- **500+ products**: Food, energy, housing, livestock, services, agricultural exports
- **Historical depth**: CPI from the 1960s, producer prices from 1991, market prices from 2010
- **Regional granularity**: National → 12 regions → 75 provinces → 18+ cities → markets
- **10+ data sources**: World Bank, FAOSTAT, HCP, WFP, news media, manual archives
- **Enterprise pipeline**: Kafka → Spark → Delta Lake → PostgreSQL → API/Superset

## Project Status

Early build (Phases 0–4). The **script-based ingestion path is working and validated end-to-end**:

| Stage | State |
|-------|-------|
| Domain core (models, ports, transformers, registry, chain) | ✅ built, 50 tests |
| Collectors — World Bank, FAOSTAT, Manual | ✅ live, plugin-registered |
| Warehouse ingestion → PostgreSQL star schema | ✅ working (`run_collectors` → `run_processing`) |
| Enrichment — unit normalization, historical FX, inflation | ✅ working |
| Kafka → Spark → Delta medallion layers | 🚧 infra defined, not yet wired end-to-end |
| Quality (Great Expectations), API routes, Superset, Airflow | ⏳ planned |

**Validated:** the live FAOSTAT sheep producer-price series (1991–1998) reproduces the documented figures exactly after unit + currency normalization (e.g. 1998 → 51.25 MAD/kg). See [`docs/sources/sheep_prices.md`](docs/sources/sheep_prices.md) and [`docs/sources/price_research_2026.md`](docs/sources/price_research_2026.md).

## Architecture

```
Collectors → Kafka → Spark → Delta Lake (Bronze/Silver/Gold) → PostgreSQL → API + Superset
                                                                              ↓
                                                                    Grafana (Metrics + Logs)
```

Three patterns, each solving a distinct problem:
- **Plugin collectors** — sources self-register via `@register_collector`; adding a source is one file.
- **Pipe-and-filter transformers** — small composable transform steps.
- **Hexagonal core** — a pure-Python domain with zero external dependencies behind ports/adapters.

See [docs/01_architecture.md](docs/01_architecture.md) for full details.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Ingestion | Apache Kafka + Schema Registry (Avro) |
| Processing | Apache Spark (PySpark) |
| Storage | Delta Lake (ACID on Parquet) |
| Catalog | Hive Metastore |
| Warehouse | PostgreSQL 16 |
| Orchestration | Apache Airflow |
| API | FastAPI |
| BI | Apache Superset |
| Quality | Great Expectations |
| Observability | Prometheus + Grafana + Loki |
| Containers | Docker + Docker Compose |

## Quick Start — run the working pipeline

The ingestion path runs today without the full Kafka/Spark stack — just PostgreSQL.

```bash
# 1. Install (dev extras include ruff, mypy, pytest)
python -m pip install -e ".[dev]"

# 2. Start the project database (published on host port 5434 to avoid clashes;
#    schema is created automatically from scripts/init_postgres.sql)
docker compose up -d postgres

# 3. Seed dimensions (products, locations, sources, calendar)
python scripts/seed_all.py

# 4. Collect from live sources → PostgreSQL, then enrich
python scripts/run_collectors.py
python scripts/run_processing.py
```

The database host port is configurable via `POSTGRES_HOST_PORT` (default `5434`); containers talk to it internally on `5432`.

## Full Stack

```bash
# Start every service (requires Docker, 32GB RAM recommended)
docker compose up -d
docker compose ps

# Spark UI: http://localhost:8080   Airflow: http://localhost:8082
# API:      http://localhost:8000   Superset: http://localhost:8088
# Grafana:  http://localhost:3000
```

## Development

```bash
ruff check . && ruff format --check .   # lint + format
mypy src scripts                        # strict type checking
pytest                                  # 50 tests
```

CI runs all of the above on every push and pull request.

## Documentation

| Document | Description |
|----------|------------|
| [Architecture](docs/01_architecture.md) | System design and data flow |
| [Data Model](docs/02_data_model.md) | Star schema, dimensions, fact table |
| [Product Catalog](docs/03_product_catalog.md) | 500+ products across 21 categories |
| [Infrastructure](docs/04_infrastructure.md) | Docker services, ports, resources |
| [Implementation Phases](docs/05_phases.md) | 10-phase build plan |
| [Logging & Observability](docs/06_logging.md) | Structured logging, metrics, alerts |
| [Data Sources](docs/sources/all_sources.md) | All 30+ sources with links |
| [2026 Price Research](docs/sources/price_research_2026.md) | Current price landscape + source verification |
| [Sheep Prices Research](docs/sources/sheep_prices.md) | Deep dive: sheep prices 1970–2026 |

## Data Sources

| Source | Data | Period | Access |
|--------|------|--------|--------|
| World Bank API | CPI, inflation | 1960–now | Free REST API |
| FAOSTAT | Producer prices (200+ commodities) | 1991–now | Free bulk CSV |
| FAOSTAT CP | General + food CPI | 2000–now | Free bulk CSV |
| HCP Morocco | CPI by 18 cities (546-article basket) | 2007–now | Free Excel |
| WFP/HDX | Market food prices | 2010–now | Free CSV |
| News media | Eid prices, market reports | 2005–now | Web scraping |
| Historical archives | Pre-1991 price points | 1960–1990 | Manual entry from PDFs |

## License

- **Code**: MIT
- **Data**: CC-BY-4.0 (attribution required)
- **Third-party data**: Subject to original source licenses (see [sources](docs/sources/all_sources.md))

## Author

[@wizli595](https://github.com/wizli595)
