# Infrastructure

## System Requirements

| Resource | Minimum | Recommended | This Project |
|----------|---------|-------------|-------------|
| RAM | 16 GB | 32 GB | **32 GB** |
| CPU | 4 cores | 8 cores | |
| Disk | 20 GB free | 50 GB free | |
| Docker | 24+ | Latest | |
| Docker Compose | v2 | Latest | |

---

## Docker Services

### Full Stack: 17 Services

```yaml
# docker-compose.yml service map

# ─── INFRASTRUCTURE ──────────────────────────────────────
#
# 1. zookeeper          Kafka coordination
# 2. kafka              Message streaming
# 3. schema-registry    Avro schema management
# 4. spark-master       Spark cluster master
# 5. spark-worker       Spark cluster worker
# 6. hive-metastore     Table/partition catalog
# 7. postgres           Shared database (3 DBs)
#
# ─── ORCHESTRATION ───────────────────────────────────────
#
# 8. airflow-webserver  DAG UI
# 9. airflow-scheduler  Job executor
#
# ─── APPLICATION ─────────────────────────────────────────
#
# 10. api               FastAPI REST API
# 11. superset          BI dashboards
#
# ─── OBSERVABILITY ───────────────────────────────────────
#
# 12. prometheus         Metrics collection
# 13. grafana            Metrics + logs dashboard
# 14. loki               Log aggregation
# 15. promtail           Docker log shipper
#
# ─── INIT (run-once) ────────────────────────────────────
#
# 16. init-kafka         Create Kafka topics
# 17. init-delta         Create Delta Lake structure
```

---

## Service Details

### Zookeeper

| Property | Value |
|----------|-------|
| Image | `confluentinc/cp-zookeeper:7.6.0` |
| Port | 2181 (internal only) |
| RAM | ~256 MB |
| Purpose | Kafka broker coordination |

### Kafka

| Property | Value |
|----------|-------|
| Image | `confluentinc/cp-kafka:7.6.0` |
| Ports | 9092 (internal), 9093 (external) |
| RAM | ~1 GB |
| Purpose | Message streaming between collectors and Spark |
| Config | `KAFKA_AUTO_CREATE_TOPICS_ENABLE=false` (explicit topic creation) |

**Topics:**

| Topic | Partitions | Retention | Purpose |
|-------|-----------|-----------|---------|
| `raw.worldbank` | 1 | 7 days | World Bank API observations |
| `raw.faostat` | 3 | 7 days | FAOSTAT bulk data (larger volume) |
| `raw.hcp` | 1 | 7 days | HCP Excel observations |
| `raw.wfp` | 1 | 7 days | WFP food prices |
| `raw.news` | 1 | 7 days | Scraped news prices |
| `raw.manual` | 1 | 30 days | Hand-entered data |
| `processed.silver` | 3 | 3 days | Silver-layer output notifications |
| `alerts.quality` | 1 | 30 days | Quality check failures |
| `alerts.anomaly` | 1 | 30 days | Anomaly detection alerts |

### Schema Registry

| Property | Value |
|----------|-------|
| Image | `confluentinc/cp-schema-registry:7.6.0` |
| Port | 8081 |
| RAM | ~512 MB |
| Purpose | Avro schema enforcement for Kafka messages |
| Compatibility | `BACKWARD` (new schemas can read old data) |

### Spark Master

| Property | Value |
|----------|-------|
| Image | `bitnami/spark:3.5` (or custom Dockerfile with Delta Lake) |
| Ports | 7077 (cluster), 8080 (Web UI) |
| RAM | ~1 GB |
| Purpose | Spark cluster coordinator |

### Spark Worker

| Property | Value |
|----------|-------|
| Image | Same as master |
| Port | 8081 (Web UI) |
| RAM | ~4 GB (`SPARK_WORKER_MEMORY=4g`) |
| Cores | `SPARK_WORKER_CORES=4` |
| Purpose | Execute Spark jobs |

**Spark Configuration:**
```
spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension
spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog
spark.sql.warehouse.dir=/data/warehouse
spark.hadoop.javax.jdo.option.ConnectionURL=jdbc:postgresql://postgres:5432/hive_metastore
```

### Hive Metastore

| Property | Value |
|----------|-------|
| Image | Custom (Apache Hive 3.x standalone metastore) |
| Port | 9083 (Thrift) |
| RAM | ~512 MB |
| Backend DB | PostgreSQL (`hive_metastore` database) |
| Purpose | Table catalog, partition management, schema registry for lakehouse |

### PostgreSQL

| Property | Value |
|----------|-------|
| Image | `postgres:16-alpine` |
| Port | 5432 (internal), 5433 (external) |
| RAM | ~512 MB |
| Purpose | Shared database server |

**Databases:**

| Database | Purpose |
|----------|---------|
| `maprix` | Serving layer - star schema for API/Superset |
| `hive_metastore` | Hive Metastore backend |
| `airflow` | Airflow metadata |
| `superset` | Superset metadata |

### Airflow Webserver

| Property | Value |
|----------|-------|
| Image | `apache/airflow:2.9-python3.12` |
| Port | 8082 (Web UI) |
| RAM | ~512 MB |
| Executor | `LocalExecutor` |
| Backend | PostgreSQL (`airflow` database) |

### Airflow Scheduler

| Property | Value |
|----------|-------|
| Image | Same as webserver |
| RAM | ~512 MB |
| Purpose | DAG execution, task scheduling |

### FastAPI

| Property | Value |
|----------|-------|
| Image | Custom Python 3.12 |
| Port | 8000 |
| RAM | ~256 MB |
| Purpose | REST API for data access and export |

### Apache Superset

| Property | Value |
|----------|-------|
| Image | `apache/superset:3.1` |
| Port | 8088 |
| RAM | ~1 GB |
| Backend | PostgreSQL (`superset` database) |
| Purpose | BI dashboards, charts, SQL exploration |

### Prometheus

| Property | Value |
|----------|-------|
| Image | `prom/prometheus:v2.51.0` |
| Port | 9090 |
| RAM | ~256 MB |
| Scrape targets | Kafka, Spark, PostgreSQL, FastAPI, Airflow |

### Grafana

| Property | Value |
|----------|-------|
| Image | `grafana/grafana:10.4.0` |
| Port | 3000 |
| RAM | ~256 MB |
| Datasources | Prometheus (metrics), Loki (logs) |

**Pre-provisioned Dashboards:**
- Pipeline Health (job status, latency, error rates)
- Data Quality (coverage, freshness, anomalies)
- Infrastructure (CPU, memory, disk, Kafka consumer lag)
- Collector Status (per-source success/failure)

### Loki

| Property | Value |
|----------|-------|
| Image | `grafana/loki:2.9.0` |
| Port | 3100 |
| RAM | ~256 MB |
| Retention | 7 days |
| Purpose | Centralized log aggregation |

### Promtail

| Property | Value |
|----------|-------|
| Image | `grafana/promtail:2.9.0` |
| RAM | ~128 MB |
| Purpose | Collects Docker container logs → ships to Loki |
| Config | Scrapes `/var/lib/docker/containers` |

---

## Resource Allocation Summary

| Service | RAM | Notes |
|---------|-----|-------|
| Zookeeper | 256 MB | |
| Kafka | 1,024 MB | |
| Schema Registry | 512 MB | |
| Spark Master | 1,024 MB | |
| Spark Worker | 4,096 MB | Main processing power |
| Hive Metastore | 512 MB | |
| PostgreSQL | 512 MB | Shared instance |
| Airflow (web + scheduler) | 1,024 MB | |
| FastAPI | 256 MB | |
| Superset | 1,024 MB | |
| Prometheus | 256 MB | |
| Grafana | 256 MB | |
| Loki | 256 MB | |
| Promtail | 128 MB | |
| **Total** | **~11 GB** | Leaves ~21 GB for OS + development |

---

## Port Map

| Port | Service | URL |
|------|---------|-----|
| 2181 | Zookeeper | Internal only |
| 5433 | PostgreSQL | `localhost:5433` |
| 7077 | Spark Master | Internal (cluster) |
| 8000 | FastAPI | http://localhost:8000 |
| 8080 | Spark UI | http://localhost:8080 |
| 8081 | Schema Registry | http://localhost:8081 |
| 8082 | Airflow | http://localhost:8082 |
| 8088 | Superset | http://localhost:8088 |
| 9083 | Hive Metastore | Internal (Thrift) |
| 9090 | Prometheus | http://localhost:9090 |
| 9093 | Kafka | `localhost:9093` |
| 3000 | Grafana | http://localhost:3000 |
| 3100 | Loki | Internal only |

---

## Volume Mounts

```yaml
volumes:
  # Data persistence
  postgres_data:        # PostgreSQL data
  kafka_data:           # Kafka message logs
  spark_data:           # Spark scratch space
  
  # Application data (bind mounts)
  ./data/bronze:        # Bronze layer (Delta Lake)
  ./data/silver:        # Silver layer (Delta Lake)
  ./data/gold:          # Gold layer (Delta Lake)
  ./data/warehouse:     # Hive warehouse directory
  ./data/checkpoints:   # Spark streaming checkpoints
  
  # Configuration (bind mounts)
  ./config/prometheus:  # prometheus.yml
  ./config/grafana:     # Datasources + dashboards
  ./config/promtail:    # promtail-config.yml
  ./config/airflow:     # DAGs, plugins
  ./config/superset:    # superset_config.py
  
  # Logs
  ./logs:               # Application logs (also captured by Docker → Promtail)
```

---

## Network

```yaml
networks:
  maprix-net:
    driver: bridge
    # All services on the same network
    # Service discovery via container names
```

---

## Profiles (Optional Service Groups)

```yaml
# docker compose --profile monitoring up
# docker compose --profile full up

profiles:
  core:         # Kafka, Spark, Postgres, Hive, Delta
  orchestration: # Airflow
  serving:      # FastAPI, Superset
  monitoring:   # Prometheus, Grafana, Loki, Promtail
  full:         # Everything
```

---

## Environment Variables (.env)

```bash
# ─── Project ────────────────────────
PROJECT_NAME=maprix
ENVIRONMENT=development

# ─── PostgreSQL ─────────────────────
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=maprix
POSTGRES_PASSWORD=changeme_in_production
POSTGRES_DB=maprix
POSTGRES_HIVE_DB=hive_metastore
POSTGRES_AIRFLOW_DB=airflow
POSTGRES_SUPERSET_DB=superset

# ─── Kafka ──────────────────────────
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081
KAFKA_NUM_PARTITIONS=3
KAFKA_REPLICATION_FACTOR=1

# ─── Spark ──────────────────────────
SPARK_MASTER_URL=spark://spark-master:7077
SPARK_WORKER_MEMORY=4g
SPARK_WORKER_CORES=4
SPARK_DRIVER_MEMORY=2g

# ─── Delta Lake ─────────────────────
DELTA_BRONZE_PATH=/data/bronze
DELTA_SILVER_PATH=/data/silver
DELTA_GOLD_PATH=/data/gold

# ─── Airflow ────────────────────────
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://maprix:changeme@postgres:5432/airflow
AIRFLOW_ADMIN_USER=admin
AIRFLOW_ADMIN_PASSWORD=admin

# ─── Superset ───────────────────────
SUPERSET_SECRET_KEY=changeme_in_production
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=admin

# ─── Grafana ────────────────────────
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin

# ─── Collectors ─────────────────────
WORLDBANK_BASE_URL=https://api.worldbank.org/v2
FAOSTAT_BULK_URL=https://bulks-faostat.fao.org
HCP_BASE_URL=https://www.hcp.ma
WFP_HDX_URL=https://data.humdata.org
COLLECTOR_USER_AGENT=MaPrix/1.0 (Morocco Price Observatory; Academic Research)
COLLECTOR_REQUEST_TIMEOUT=30
COLLECTOR_RETRY_MAX=3
COLLECTOR_RETRY_DELAY=5

# ─── Logging ────────────────────────
LOG_LEVEL=INFO
LOG_FORMAT=json
LOKI_URL=http://loki:3100
```

---

## Health Checks

Every service in docker-compose.yml should have a health check:

```yaml
kafka:
  healthcheck:
    test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
    interval: 30s
    timeout: 10s
    retries: 5

postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U maprix"]
    interval: 10s
    timeout: 5s
    retries: 5

spark-master:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080"]
    interval: 30s
    timeout: 10s
    retries: 3

api:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 15s
    timeout: 5s
    retries: 3
```

---

## Startup Order (depends_on)

```
1. postgres           (no dependencies)
2. zookeeper          (no dependencies)
3. kafka              (depends: zookeeper)
4. schema-registry    (depends: kafka)
5. hive-metastore     (depends: postgres)
6. spark-master       (depends: hive-metastore)
7. spark-worker       (depends: spark-master)
8. init-kafka         (depends: schema-registry) [run-once]
9. init-delta         (depends: spark-master) [run-once]
10. airflow-scheduler (depends: postgres, kafka, spark-master)
11. airflow-webserver (depends: airflow-scheduler)
12. api               (depends: postgres)
13. superset          (depends: postgres)
14. loki              (no dependencies)
15. promtail          (depends: loki)
16. prometheus        (no dependencies)
17. grafana           (depends: prometheus, loki)
```
