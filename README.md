# MaPrix - Morocco Price Observatory

An enterprise-grade data platform that collects, processes, and serves historical and current price data for Morocco — from a loaf of khobz to a head of sheep.

## Why This Exists

No unified dataset exists for Moroccan prices. Data is scattered across 30+ sources in 3 languages — behind APIs, in Excel files, in PDFs, in news articles. This project unifies it all into a single, queryable, versioned dataset.

## What's Inside

- **500+ products**: Food, energy, housing, livestock, services, agricultural exports
- **Historical depth**: CPI from 1960s, producer prices from 1991, market prices from 2010
- **Regional granularity**: National → 12 regions → 75 provinces → 18+ cities → markets
- **10+ data sources**: World Bank, FAOSTAT, HCP, WFP, news media, manual archives
- **Enterprise pipeline**: Kafka → Spark → Delta Lake → PostgreSQL → API/Superset

## Architecture

```
Collectors → Kafka → Spark → Delta Lake (Bronze/Silver/Gold) → PostgreSQL → API + Superset
                                                                              ↓
                                                                    Grafana (Metrics + Logs)
```

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

## Quick Start

```bash
# Clone
git clone https://github.com/wizli595/morocco-prices.git
cd morocco-prices

# Start all services (requires Docker, 32GB RAM recommended)
docker compose up -d

# Check services
docker compose ps

# Access
# Spark UI:    http://localhost:8080
# Airflow:     http://localhost:8082
# API:         http://localhost:8000
# Superset:    http://localhost:8088
# Grafana:     http://localhost:3000
```

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
| [Sheep Prices Research](docs/sources/sheep_prices.md) | Deep dive: sheep prices 1970-2026 |

## Data Sources

| Source | Data | Period | Access |
|--------|------|--------|--------|
| World Bank API | CPI, inflation | 1960-now | Free REST API |
| FAOSTAT | Producer prices (200+ commodities) | 1991-now | Free bulk CSV |
| HCP Morocco | CPI by 18 cities | 2007-now | Free Excel |
| WFP/HDX | Market food prices | 2010-now | Free CSV |
| News media | Eid prices, market reports | 2005-now | Web scraping |
| Historical archives | Pre-1991 price points | 1960-1990 | Manual entry from PDFs |

## License

- **Code**: MIT
- **Data**: CC-BY-4.0 (attribution required)
- **Third-party data**: Subject to original source licenses (see [sources](docs/sources/all_sources.md))

## Author

[@wizli595](https://github.com/wizli595)
