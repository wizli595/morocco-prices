-- Initialize all PostgreSQL databases for MaPrix

CREATE DATABASE hive_metastore;
CREATE DATABASE airflow;
CREATE DATABASE superset;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE hive_metastore TO maprix;
GRANT ALL PRIVILEGES ON DATABASE airflow TO maprix;
GRANT ALL PRIVILEGES ON DATABASE superset TO maprix;

-- Serving schema in the main maprix database
\c maprix;

CREATE SCHEMA IF NOT EXISTS serving;

CREATE TABLE IF NOT EXISTS serving.dim_product (
    product_key     SERIAL PRIMARY KEY,
    product_id      VARCHAR(100) UNIQUE NOT NULL,
    category        VARCHAR(50)  NOT NULL,
    subcategory     VARCHAR(50)  NOT NULL,
    product_name    VARCHAR(100) NOT NULL,
    variety         VARCHAR(100),
    name_en         VARCHAR(200) NOT NULL,
    name_fr         VARCHAR(200) NOT NULL,
    name_ar         VARCHAR(200),
    canonical_unit  VARCHAR(30)  NOT NULL,
    is_subsidized   BOOLEAN DEFAULT FALSE,
    is_seasonal     BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS serving.dim_location (
    location_key    SERIAL PRIMARY KEY,
    location_id     VARCHAR(100) UNIQUE NOT NULL,
    country         VARCHAR(50)  NOT NULL DEFAULT 'Morocco',
    region          VARCHAR(100),
    province        VARCHAR(100),
    city            VARCHAR(100),
    market          VARCHAR(200),
    level           VARCHAR(20)  NOT NULL,
    latitude        DECIMAL(10,7),
    longitude       DECIMAL(10,7)
);

CREATE TABLE IF NOT EXISTS serving.dim_source (
    source_key      SERIAL PRIMARY KEY,
    source_id       VARCHAR(50) UNIQUE NOT NULL,
    source_name     VARCHAR(200) NOT NULL,
    organization    VARCHAR(200) NOT NULL,
    source_type     VARCHAR(20)  NOT NULL,
    reliability     VARCHAR(20)  NOT NULL,
    url             VARCHAR(500),
    priority_rank   INT NOT NULL
);

CREATE TABLE IF NOT EXISTS serving.dim_time (
    time_key        INT PRIMARY KEY,
    date            DATE,
    year            INT NOT NULL,
    month           INT,
    day             INT,
    quarter         INT,
    grain           VARCHAR(10) NOT NULL,
    season          VARCHAR(10),
    is_ramadan      BOOLEAN DEFAULT FALSE,
    is_eid_adha     BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS serving.fact_prices (
    observation_id      VARCHAR(64) PRIMARY KEY,
    product_key         INT REFERENCES serving.dim_product(product_key),
    location_key        INT REFERENCES serving.dim_location(location_key),
    time_key            INT REFERENCES serving.dim_time(time_key),
    source_key          INT REFERENCES serving.dim_source(source_key),
    original_value      DECIMAL(15,4),
    original_min        DECIMAL(15,4),
    original_max        DECIMAL(15,4),
    original_unit       VARCHAR(50),
    original_currency   VARCHAR(10),
    price_mad           DECIMAL(15,4),
    price_usd           DECIMAL(15,4),
    price_real_mad      DECIMAL(15,4),
    confidence          VARCHAR(20),
    precision           VARCHAR(20),
    collection_method   VARCHAR(20),
    pipeline_run_id     VARCHAR(64),
    ingested_at         TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fact_product   ON serving.fact_prices(product_key);
CREATE INDEX idx_fact_location  ON serving.fact_prices(location_key);
CREATE INDEX idx_fact_time      ON serving.fact_prices(time_key);
CREATE INDEX idx_fact_source    ON serving.fact_prices(source_key);
