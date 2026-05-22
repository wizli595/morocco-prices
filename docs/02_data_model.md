# Data Model

## Overview

The Morocco Price Observatory uses a **star schema** dimensional model. This is the industry standard for analytical workloads - optimized for aggregation queries, filtering, and BI tools like Superset.

```
                          ┌──────────────┐
                          │  dim_product  │
                          └──────┬───────┘
                                 │
  ┌──────────────┐    ┌─────────┴──────────┐    ┌───────────────┐
  │ dim_location  │◄──│   fact_prices       │──►│  dim_source    │
  └──────────────┘    │   (central fact)    │    └───────────────┘
                       │                    │
  ┌──────────────┐    │                    │    ┌───────────────┐
  │  dim_time     │◄──│                    │──►│ dim_price_type │
  └──────────────┘    └────────────────────┘    └───────────────┘
```

---

## Fact Table: fact_prices

The central table. Every row is a single price observation.

```sql
CREATE TABLE fact_prices (
    -- Primary key (deterministic hash)
    observation_id      VARCHAR(64) PRIMARY KEY,
    -- SHA256(product_id || location_id || time_key || source_id || price_type_id)
    
    -- Foreign keys to dimensions
    product_key         INT         NOT NULL REFERENCES dim_product(product_key),
    location_key        INT         NOT NULL REFERENCES dim_location(location_key),
    time_key            INT         NOT NULL REFERENCES dim_time(time_key),
    source_key          INT         NOT NULL REFERENCES dim_source(source_key),
    price_type_key      INT         NOT NULL REFERENCES dim_price_type(price_type_key),
    
    -- Original values (immutable, as reported by source)
    original_value      DECIMAL(15,4),          -- Exact value if available
    original_min        DECIMAL(15,4),          -- Lower bound if range ("3000-7000")
    original_max        DECIMAL(15,4),          -- Upper bound if range
    original_unit       VARCHAR(50)  NOT NULL,  -- "MAD/tonne", "DH/kg", "USD/tonne"
    original_currency   VARCHAR(10)  NOT NULL,  -- "MAD", "USD", "EUR"
    
    -- Normalized values (computed by pipeline)
    price_mad           DECIMAL(15,4),          -- Canonical unit, in MAD
    price_usd           DECIMAL(15,4),          -- USD at historical exchange rate
    price_real_mad      DECIMAL(15,4),          -- Inflation-adjusted MAD (base 2017)
    price_min_mad       DECIMAL(15,4),          -- Normalized range lower bound
    price_max_mad       DECIMAL(15,4),          -- Normalized range upper bound
    
    -- Quality metadata
    confidence          VARCHAR(20)  NOT NULL,
        -- "official"       : Government/institutional exact data
        -- "institutional"  : International org (FAO, World Bank)
        -- "estimated"      : Derived from index or calculation
        -- "reconstructed"  : Gap-filled via interpolation
        -- "journalistic"   : From news reporting
        -- "anecdotal"      : Forum, social media, informal
        
    precision           VARCHAR(20)  NOT NULL,
        -- "exact"          : Single precise number
        -- "range"          : Min-max range reported
        -- "approximate"    : Rounded or estimated number
        -- "index_derived"  : Reconstructed from price index + anchor
        
    collection_method   VARCHAR(20)  NOT NULL,
        -- "api"            : REST API call
        -- "file_download"  : Bulk file (CSV, Excel)
        -- "scrape"         : Web scraping
        -- "manual"         : Hand-entered from document/PDF
        -- "calculated"     : Derived from other observations
        
    interpolation_method VARCHAR(30),
        -- NULL             : Not interpolated (direct observation)
        -- "index_anchor"   : Price = anchor_price * (index_current / index_anchor)
        -- "linear"         : Linear interpolation between known points
        -- "source_crossref": Inferred from another source's data
    
    -- Lineage
    pipeline_run_id     VARCHAR(64)  NOT NULL,
    ingested_at         TIMESTAMP    NOT NULL,
    processed_at        TIMESTAMP    NOT NULL
);

-- Indexes for common query patterns
CREATE INDEX idx_fact_product      ON fact_prices(product_key);
CREATE INDEX idx_fact_location     ON fact_prices(location_key);
CREATE INDEX idx_fact_time         ON fact_prices(time_key);
CREATE INDEX idx_fact_source       ON fact_prices(source_key);
CREATE INDEX idx_fact_confidence   ON fact_prices(confidence);

-- Delta Lake partitioning (for Parquet storage)
-- PARTITIONED BY (category STRING, year INT)
```

### Observation ID Generation

```python
import hashlib

def make_observation_id(
    product_id: str,     # "MEAT-SHEEP-SARDI"
    location_id: str,    # "MA-NATIONAL" or "MA-CAS-DERB_SULTAN"
    time_key: int,       # 20240601
    source_id: str,      # "FAOSTAT"
    price_type_id: str   # "PRODUCER-MAD_TONNE"
) -> str:
    raw = f"{product_id}|{location_id}|{time_key}|{source_id}|{price_type_id}"
    return hashlib.sha256(raw.encode()).hexdigest()
```

---

## Dimension: dim_product

Hierarchical product taxonomy (4 levels).

```sql
CREATE TABLE dim_product (
    product_key     SERIAL PRIMARY KEY,             -- Surrogate key
    product_id      VARCHAR(100) UNIQUE NOT NULL,   -- Natural key: "MEAT-SHEEP-SARDI"
    
    -- Hierarchy (Level 1 → Level 4)
    category        VARCHAR(50)  NOT NULL,   -- L1: "Cereals", "Meat", "Dairy", "Energy"
    subcategory     VARCHAR(50)  NOT NULL,   -- L2: "Red Meat", "Poultry", "Seafood"
    product_name    VARCHAR(100) NOT NULL,   -- L3: "Sheep", "Beef", "Chicken"
    variety         VARCHAR(100),            -- L4: "Sardi", "Bergui" (nullable)
    
    -- Multilingual names
    name_en         VARCHAR(200) NOT NULL,
    name_fr         VARCHAR(200) NOT NULL,
    name_ar         VARCHAR(200),
    name_darija     VARCHAR(200),            -- Moroccan Arabic (spoken names)
    
    -- Attributes
    is_subsidized   BOOLEAN DEFAULT FALSE,   -- Bread, sugar, butane, flour
    is_seasonal     BOOLEAN DEFAULT FALSE,   -- Watermelon, dates, etc.
    peak_season     VARCHAR(20),             -- "JUN-AUG" for watermelon
    is_imported     BOOLEAN DEFAULT FALSE,   -- Mostly imported products
    is_exported     BOOLEAN DEFAULT FALSE,   -- Morocco exports this
    
    -- Cross-reference codes
    canonical_unit  VARCHAR(30)  NOT NULL,   -- "MAD/kg", "MAD/L", "MAD/unit"
    faostat_code    VARCHAR(20),             -- FAO item code (e.g., "977")
    hcp_code        VARCHAR(20),             -- HCP IPC basket code
    hs_code         VARCHAR(20),             -- Harmonized System trade code
    
    -- Metadata
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

### Product Hierarchy Example

```
category=Meat
├── subcategory=Red Meat
│   ├── product_name=Sheep
│   │   ├── variety=Sardi          → product_id=MEAT-SHEEP-SARDI
│   │   ├── variety=Bergui         → product_id=MEAT-SHEEP-BERGUI
│   │   ├── variety=Timahdite      → product_id=MEAT-SHEEP-TIMAHDITE
│   │   ├── variety=Beni Guil      → product_id=MEAT-SHEEP-BENIGUIL
│   │   ├── variety=D'man          → product_id=MEAT-SHEEP-DMAN
│   │   ├── variety=Imported       → product_id=MEAT-SHEEP-IMPORTED
│   │   └── variety=NULL (generic) → product_id=MEAT-SHEEP
│   ├── product_name=Beef
│   │   ├── variety=Local          → product_id=MEAT-BEEF-LOCAL
│   │   └── variety=Imported       → product_id=MEAT-BEEF-IMPORTED
│   └── product_name=Goat          → product_id=MEAT-GOAT
├── subcategory=Poultry
│   ├── product_name=Chicken
│   │   ├── variety=Broiler        → product_id=MEAT-CHICKEN-BROILER
│   │   └── variety=Beldi          → product_id=MEAT-CHICKEN-BELDI
│   └── product_name=Turkey        → product_id=MEAT-TURKEY
├── subcategory=Offal
│   ├── product_name=Liver         → product_id=MEAT-OFFAL-LIVER
│   ├── product_name=Tripe         → product_id=MEAT-OFFAL-TRIPE
│   └── product_name=Heart         → product_id=MEAT-OFFAL-HEART
└── subcategory=Processed
    ├── product_name=Kefta          → product_id=MEAT-PROC-KEFTA
    └── product_name=Merguez        → product_id=MEAT-PROC-MERGUEZ
```

---

## Dimension: dim_location

Morocco's administrative hierarchy (5 levels).

```sql
CREATE TABLE dim_location (
    location_key    SERIAL PRIMARY KEY,
    location_id     VARCHAR(100) UNIQUE NOT NULL,   -- "MA-CAS" or "MA-CAS-DERB_SULTAN"
    
    -- Hierarchy (Level 1 → Level 5)
    country         VARCHAR(50)  NOT NULL DEFAULT 'Morocco',
    region          VARCHAR(100),            -- 12 regions
    province        VARCHAR(100),            -- 75 provinces/prefectures
    city            VARCHAR(100),            -- City/town
    market          VARCHAR(200),            -- Specific souk/market (nullable)
    
    -- Granularity indicator
    level           VARCHAR(20)  NOT NULL,
        -- "national"   : Country-level aggregate
        -- "regional"   : One of 12 regions
        -- "provincial" : One of 75 provinces
        -- "city"       : City/town level
        -- "market"     : Specific market/souk
    
    -- Geo
    latitude        DECIMAL(10,7),
    longitude       DECIMAL(10,7),
    
    -- Cross-reference codes
    hcp_code        VARCHAR(20),             -- HCP region/city code
    iso_3166_2      VARCHAR(10),             -- "MA-CAS", "MA-RAB"
    
    -- Attributes
    population      INT,                     -- Latest census
    is_urban        BOOLEAN,
    
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### Location Hierarchy

```
country=Morocco (MA-NATIONAL)
├── region=Casablanca-Settat (MA-R06)
│   ├── province=Casablanca (MA-R06-CAS)
│   │   ├── city=Casablanca (MA-CAS)
│   │   │   ├── market=Marché de gros Casa (MA-CAS-GROS)
│   │   │   ├── market=Derb Sultan (MA-CAS-DERB_SULTAN)
│   │   │   └── market=Hay Mohammadi (MA-CAS-HAY_MOHAMMADI)
│   │   └── city=Mohammedia (MA-MOH)
│   └── province=Settat (MA-R06-SET)
│       └── city=Settat (MA-SET)
├── region=Rabat-Salé-Kénitra (MA-R04)
│   ├── city=Rabat (MA-RAB)
│   ├── city=Salé (MA-SAL)
│   └── city=Kénitra (MA-KEN)
├── region=Fès-Meknès (MA-R03)
│   ├── city=Fès (MA-FES)
│   └── city=Meknès (MA-MEK)
├── region=Marrakech-Safi (MA-R07)
│   ├── city=Marrakech (MA-MAR)
│   └── city=Safi (MA-SAF)
├── region=Tanger-Tétouan-Al Hoceïma (MA-R01)
│   ├── city=Tanger (MA-TNG)
│   ├── city=Tétouan (MA-TET)
│   └── city=Al Hoceïma (MA-HOC)
├── region=L'Oriental (MA-R02)
│   └── city=Oujda (MA-OUJ)
├── region=Béni Mellal-Khénifra (MA-R05)
│   └── city=Béni Mellal (MA-BEN)
├── region=Drâa-Tafilalet (MA-R08)
│   └── city=Errachidia (MA-ERR)
├── region=Souss-Massa (MA-R09)
│   └── city=Agadir (MA-AGA)
├── region=Guelmim-Oued Noun (MA-R10)
│   └── city=Guelmim (MA-GUE)
├── region=Laâyoune-Sakia El Hamra (MA-R11)
│   └── city=Laâyoune (MA-LAA)
└── region=Dakhla-Oued Ed-Dahab (MA-R12)
    └── city=Dakhla (MA-DAK)
```

---

## Dimension: dim_time

Calendar dimension with Morocco-specific context.

```sql
CREATE TABLE dim_time (
    time_key        INT PRIMARY KEY,
        -- Format: YYYYMMDD for daily, YYYYMM00 for monthly, YYYY0000 for annual
    
    date            DATE,                   -- NULL for month/year-only
    year            INT          NOT NULL,
    month           INT,                    -- NULL for annual observations
    day             INT,                    -- NULL for month/year observations
    
    quarter         INT,                    -- 1-4
    week_of_year    INT,
    day_of_week     INT,                    -- 1=Monday ... 7=Sunday
    
    -- Temporal grain
    grain           VARCHAR(10)  NOT NULL,
        -- "daily" | "weekly" | "monthly" | "quarterly" | "annual"
    
    -- Morocco calendar context
    season          VARCHAR(10),
        -- "spring" (Mar-May) | "summer" (Jun-Aug) 
        -- "autumn" (Sep-Nov) | "winter" (Dec-Feb)
    
    agricultural_season VARCHAR(10),         -- "2023/2024" (Sep-Aug cycle)
    
    -- Islamic calendar events (dates shift ~11 days/year)
    is_ramadan      BOOLEAN DEFAULT FALSE,
    is_eid_fitr     BOOLEAN DEFAULT FALSE,  -- End of Ramadan
    is_eid_adha     BOOLEAN DEFAULT FALSE,  -- Sacrifice feast
    is_mawlid       BOOLEAN DEFAULT FALSE,  -- Prophet's birthday
    
    -- Agricultural events
    is_wheat_harvest    BOOLEAN DEFAULT FALSE,  -- Jun-Jul
    is_olive_harvest    BOOLEAN DEFAULT FALSE,  -- Nov-Jan
    is_citrus_season    BOOLEAN DEFAULT FALSE,  -- Nov-Mar
    is_date_harvest     BOOLEAN DEFAULT FALSE,  -- Oct-Nov
    
    -- Economic context
    fiscal_year     INT,                    -- = calendar year in Morocco
    
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### Time Key Examples

| Observation | time_key | grain |
|------------|---------|-------|
| Annual 2024 | 20240000 | annual |
| March 2024 | 20240300 | monthly |
| March 15, 2024 | 20240315 | daily |
| Q1 2024 | 20240100 | quarterly |

---

## Dimension: dim_source

```sql
CREATE TABLE dim_source (
    source_key      SERIAL PRIMARY KEY,
    source_id       VARCHAR(50) UNIQUE NOT NULL,     -- "FAOSTAT", "HCP", "WORLDBANK"
    
    source_name     VARCHAR(200) NOT NULL,           -- "FAOSTAT Producer Prices"
    organization    VARCHAR(200) NOT NULL,           -- "FAO"
    source_type     VARCHAR(20)  NOT NULL,
        -- "api"       : REST API (World Bank, IMF)
        -- "bulk_file" : Downloadable file (FAOSTAT CSV, HCP Excel)
        -- "scrape"    : Web scraping (news, Numbeo)
        -- "manual"    : Hand-entered (historical PDFs)
    
    reliability     VARCHAR(20) NOT NULL,
        -- "official"       : Moroccan government (HCP, ONCA, Bank Al-Maghrib)
        -- "institutional"  : International orgs (FAO, World Bank, IMF, WFP)
        -- "commercial"     : Commercial data providers (Selina Wamucii, Numbeo)
        -- "journalistic"   : News media (Medias24, Hespress, Le360)
        -- "academic"       : Research papers, INRA reports
        -- "anecdotal"      : Forums, social media
    
    -- Source details
    url             VARCHAR(500),
    language        VARCHAR(10),                     -- "en", "fr", "ar"
    update_frequency VARCHAR(20),                    -- "annual", "monthly", "weekly", "irregular"
    license         VARCHAR(100),                    -- "CC-BY-4.0", etc.
    
    -- Coverage
    time_range_start INT,                            -- Earliest year available
    time_range_end   INT,                            -- Latest year available
    geographic_scope VARCHAR(50),                    -- "national", "city", "market"
    
    -- Priority (for conflict resolution)
    priority_rank   INT NOT NULL,                    -- 1 = highest priority
        -- 1: HCP (official Moroccan stats)
        -- 2: FAOSTAT (international standard)
        -- 3: World Bank / IMF
        -- 4: WFP
        -- 5: Commercial providers
        -- 6: News media
        -- 7: Academic papers
        -- 8: Manual/anecdotal
    
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

---

## Dimension: dim_price_type

```sql
CREATE TABLE dim_price_type (
    price_type_key    SERIAL PRIMARY KEY,
    price_type_id     VARCHAR(50) UNIQUE NOT NULL,   -- "RETAIL-MAD_KG"
    
    price_type        VARCHAR(30) NOT NULL,
        -- "retail"      : Consumer/market price
        -- "wholesale"   : Wholesale/gros market
        -- "producer"    : Farm-gate / producer price
        -- "farmgate"    : Synonym for producer (some sources use this)
        -- "import"      : CIF import price
        -- "export"      : FOB export price
        -- "subsidized"  : Government-set subsidized price
        -- "index"       : Price index (not an actual price)
    
    unit              VARCHAR(30) NOT NULL,
        -- Weight: "MAD/kg", "MAD/tonne", "MAD/quintal"
        -- Volume: "MAD/L", "MAD/m3"
        -- Count:  "MAD/unit", "MAD/head", "MAD/dozen"
        -- Area:   "MAD/m2", "MAD/ha"
        -- Energy: "MAD/kWh", "MAD/bonbonne"
        -- Index:  "index_point"
        -- Currency: "USD/tonne", "EUR/tonne"
    
    canonical_unit    VARCHAR(30) NOT NULL,           -- What we normalize to
    conversion_factor DECIMAL(15,6) DEFAULT 1.0,     -- original × factor = canonical
        -- e.g., MAD/tonne → MAD/kg: factor = 0.001
        -- e.g., MAD/quintal → MAD/kg: factor = 0.01
    
    created_at        TIMESTAMP DEFAULT NOW()
);
```

### Common Conversions

| From | To (Canonical) | Factor |
|------|---------------|--------|
| MAD/tonne | MAD/kg | 0.001 |
| MAD/quintal | MAD/kg | 0.01 |
| USD/tonne | USD/kg | 0.001 |
| MAD/dozen (eggs) | MAD/unit | 0.0833 |
| index_point | index_point | 1.0 (no conversion) |

---

## Bronze Layer Schemas

Each source keeps its native schema in bronze. No normalization.

### bronze_worldbank

```
area_code       STRING      -- "MAR"
indicator_code  STRING      -- "FP.CPI.TOTL"
indicator_name  STRING      -- "Consumer price index (2010 = 100)"
year            INT
value           DOUBLE
decimal         INT
source_file     STRING      -- Pipeline lineage
ingested_at     TIMESTAMP
pipeline_run_id STRING

PARTITIONED BY (indicator_code STRING, year INT)
```

### bronze_faostat

```
area_code       INT         -- 143 (Morocco in FAOSTAT)
area            STRING      -- "Morocco"
item_code       INT         -- 977 (Meat of sheep)
item            STRING      -- "Meat of sheep, fresh or chilled"
element_code    INT         -- 5532 (Producer Price USD/tonne)
element         STRING      -- "Producer Price (USD/tonne)"
year            INT
value           DOUBLE
unit            STRING      -- "USD" or "LCU"
flag            STRING      -- "A" (official), "E" (estimated), etc.
note            STRING
source_file     STRING
ingested_at     TIMESTAMP
pipeline_run_id STRING

PARTITIONED BY (item_code INT, year INT)
```

### bronze_hcp

```
city            STRING      -- "Casablanca"
division_code   STRING      -- HCP division code
division        STRING      -- "Produits alimentaires"
index_value     DOUBLE      -- 122.5
base_year       INT         -- 2017
month           INT
year            INT
raw_filename    STRING      -- Original Excel filename
ingested_at     TIMESTAMP
pipeline_run_id STRING

PARTITIONED BY (year INT, month INT)
```

### bronze_wfp

```
country         STRING      -- "Morocco"
adm1            STRING      -- Administrative region
market          STRING      -- Market name
commodity       STRING      -- "Wheat flour"
year            INT
month           INT
price           DOUBLE
currency        STRING      -- "MAD"
unit            STRING      -- "KG"
source          STRING      -- "WFP"
ingested_at     TIMESTAMP
pipeline_run_id STRING

PARTITIONED BY (year INT)
```

### bronze_news

```
url             STRING
source_name     STRING      -- "Medias24", "Hespress", etc.
publish_date    DATE
headline        STRING
excerpt         STRING      -- Relevant text snippet
price_text      STRING      -- Raw price mention: "entre 3000 et 7000 DH"
price_min       DOUBLE      -- Parsed: 3000
price_max       DOUBLE      -- Parsed: 7000
item_mentioned  STRING      -- "mouton", "viande ovine"
unit_mentioned  STRING      -- "DH/kg", "DH/tête"
city_mentioned  STRING      -- "Casablanca" (nullable)
language        STRING      -- "fr", "ar"
scraped_at      TIMESTAMP
pipeline_run_id STRING

PARTITIONED BY (year INT)
```

### bronze_manual

```
year            INT
month           INT         -- nullable
item            STRING      -- "Sheep meat"
price_value     DOUBLE
price_unit      STRING      -- "MAD/kg"
source_document STRING      -- "FAO Small Ruminants in the Near East, 1987"
page_reference  STRING      -- "Chapter 5, Table 3"
notes           STRING
entered_by      STRING
entered_at      TIMESTAMP
pipeline_run_id STRING
```

---

## Silver Layer Schema

All sources converge to one unified schema (same as fact_prices but with natural keys instead of surrogate keys).

```
-- silver/prices/ (Delta Lake table)

observation_id          STRING      -- Deterministic hash
product_id              STRING      -- "MEAT-SHEEP-SARDI"
location_id             STRING      -- "MA-NATIONAL"
time_key                INT         -- 20240000
source_id               STRING      -- "FAOSTAT"
price_type_id           STRING      -- "PRODUCER-MAD_KG"

original_value          DOUBLE
original_min            DOUBLE
original_max            DOUBLE
original_unit           STRING
original_currency       STRING

price_mad               DOUBLE
price_usd               DOUBLE
price_real_mad          DOUBLE
price_min_mad           DOUBLE
price_max_mad           DOUBLE

confidence              STRING
precision               STRING
collection_method       STRING
interpolation_method    STRING

pipeline_run_id         STRING
ingested_at             TIMESTAMP
processed_at            TIMESTAMP

PARTITIONED BY (category STRING, year INT)
```

---

## Gold Layer: Pre-Aggregated Views

### agg_annual_national

```sql
-- Yearly national average per product
SELECT
    year,
    product_id,
    product_name,
    category,
    AVG(price_mad) as avg_price_mad,
    MIN(price_mad) as min_price_mad,
    MAX(price_mad) as max_price_mad,
    COUNT(*) as observation_count,
    MODE(confidence) as primary_confidence
FROM fact_prices
JOIN dim_product USING (product_key)
JOIN dim_time USING (time_key)
JOIN dim_location USING (location_key)
WHERE location.level = 'national'
GROUP BY year, product_id, product_name, category
```

### agg_monthly_city

```sql
-- Monthly price per product per city (where available)
SELECT
    year, month,
    city,
    product_id, product_name,
    AVG(price_mad) as avg_price_mad,
    COUNT(*) as observation_count
FROM fact_prices
JOIN dim_product USING (product_key)
JOIN dim_time USING (time_key)
JOIN dim_location USING (location_key)
WHERE location.level IN ('city', 'market')
GROUP BY year, month, city, product_id, product_name
```

### agg_eid_prices

```sql
-- Special view: Eid Al Adha sheep prices by year
SELECT
    year,
    city,
    variety,
    price_mad as price_per_head,
    price_min_mad,
    price_max_mad,
    source_id,
    confidence
FROM fact_prices
JOIN dim_product USING (product_key)
JOIN dim_time USING (time_key)
JOIN dim_location USING (location_key)
WHERE product.category = 'Livestock'
  AND product.product_name = 'Sheep'
  AND dim_time.is_eid_adha = TRUE
ORDER BY year, city
```

### coverage_matrix

```sql
-- What data exists where
SELECT
    product.category,
    product.product_name,
    dim_time.year,
    location.level as geo_level,
    COUNT(*) as observations,
    COUNT(DISTINCT source.source_id) as source_count,
    ARRAY_AGG(DISTINCT confidence) as confidence_levels
FROM fact_prices
JOIN dim_product USING (product_key)
JOIN dim_time USING (time_key)
JOIN dim_location USING (location_key)
JOIN dim_source USING (source_key)
GROUP BY 1, 2, 3, 4
```

---

## Exchange Rate & Inflation Tables

### ref_exchange_rates

```sql
-- Historical MAD exchange rates (for currency conversion)
CREATE TABLE ref_exchange_rates (
    year            INT,
    month           INT,        -- nullable for annual rates
    currency_from   VARCHAR(3), -- "USD", "EUR"
    currency_to     VARCHAR(3), -- "MAD"
    rate            DECIMAL(15,6),
    source          VARCHAR(50),
    PRIMARY KEY (year, month, currency_from, currency_to)
);
```

### ref_cpi_index

```sql
-- CPI index for inflation adjustment
CREATE TABLE ref_cpi_index (
    year            INT,
    month           INT,        -- nullable for annual
    base_year       INT,        -- 2017
    index_value     DECIMAL(10,4),
    source          VARCHAR(50),
    PRIMARY KEY (year, month, base_year)
);
```

---

## Estimated Row Counts

| Table | Estimated Rows | Growth Rate |
|-------|---------------|-------------|
| fact_prices | 500K - 2M | ~50K/year as more sources added |
| dim_product | ~500 | Slow (new products rare) |
| dim_location | ~200 | Static |
| dim_time | ~25,000 | ~365/year (daily grain) |
| dim_source | ~20 | Slow |
| dim_price_type | ~50 | Static |
| ref_exchange_rates | ~2,000 | ~12/year |
| ref_cpi_index | ~2,000 | ~12/year |
