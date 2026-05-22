# CLAUDE.md - Project Rules & Conventions

## Project: MaPrix (Morocco Price Observatory)

---

## Git Workflow

### Commits
- **NO co-author lines.** Ever. No `Co-Authored-By` in any commit.
- Commit messages are **human sentences**, not generated text.
- Format: `<type>: <what changed and why>`
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `infra`, `chore`
- Good:
  ```
  feat: add worldbank collector with CPI and inflation endpoints
  fix: handle missing months in HCP excel parser
  refactor: extract price normalization into dedicated transformer
  ```
- Bad (never):
  ```
  update files
  fix stuff
  WIP
  misc changes
  ```
- One commit = one thing. If you need "and", split the commit.

### Branching & PRs
- Every change: **Issue → Branch → PR → Merge**
- Branch naming: `<type>/<short-desc>` (e.g., `feat/worldbank-collector`)
- PR must have: clear title, summary, test plan.
- Merge to `main` only. Delete branch after merge.

---

## Architecture: Plugin + Pipe-and-Filter + Hexagonal

Three patterns combined. Each solves a different problem.

### Pattern 1: Plugin Architecture (Collectors)

Collectors self-register via decorator. No if/elif chains. Adding a source = adding one file.

```python
@register_collector("worldbank")
class WorldBankCollector(BaseCollector):
    def collect(self) -> list[RawObservation]: ...

@register_collector("faostat")
class FAOSTATCollector(BaseCollector):
    def collect(self) -> list[RawObservation]: ...

# Runtime — zero conditionals:
collector = CollectorRegistry.get("worldbank")
```

### Pattern 2: Pipe-and-Filter (Transformations)

Each transformation is a small class. Chain them. No nested ifs.

```python
silver_chain = TransformChain([
    ValidateSchema(),
    Deduplicate(),
    NormalizeUnit(),
    ConvertCurrency(),
    FlagOutliers(),
])
result = silver_chain.execute(bronze_data)
```

Adding a transformer = one new file + add to chain config.

### Pattern 3: Hexagonal / Ports & Adapters (Core isolation)

```
┌──────────────────────────────────┐
│         DOMAIN CORE              │
│                                  │
│  models/     (dataclasses)       │
│  transformers/ (pure functions)  │
│  quality/    (validation rules)  │
│  ports/      (ABCs)              │
│                                  │
│  ZERO external deps.             │
│  No Spark. No Kafka. No HTTP.    │
│  Pure Python only.               │
└──────────────┬───────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Inbound │ │Storage │ │Outbound│
│Adapters│ │Adapters│ │Adapters│
│        │ │        │ │        │
│Kafka   │ │Delta   │ │FastAPI │
│HTTP    │ │Postgres│ │Superset│
│Excel   │ │Hive    │ │Kaggle  │
└────────┘ └────────┘ └────────┘
```

**Rules:**
1. Domain core imports nothing external. Pure Python + stdlib.
2. Ports are ABCs that define contracts.
3. Adapters implement ports with real I/O.
4. Dependencies point inward. Never outward.
5. Domain tests need zero mocks.

---

## Code Organization

```
src/
├── core/                        # Domain — ZERO external deps
│   ├── ports/                   # Abstract contracts
│   │   ├── collector.py         # BaseCollector ABC (~20 lines)
│   │   ├── transformer.py       # BaseTransformer ABC (~15 lines)
│   │   ├── storage.py           # BaseStorage ABC (~20 lines)
│   │   └── publisher.py         # BasePublisher ABC (~15 lines)
│   ├── models/                  # Immutable domain objects
│   │   ├── observation.py       # RawObservation (~30 lines)
│   │   ├── price.py             # CleanPrice, PriceRecord (~30 lines)
│   │   ├── dimensions.py        # Product, Location, Source (~40 lines)
│   │   ├── enums.py             # Category, Confidence, Unit (~40 lines)
│   │   └── errors.py            # Exception hierarchy (~25 lines)
│   ├── transformers/            # Pure logic, no I/O
│   │   ├── unit_normalizer.py   # (~40 lines)
│   │   ├── price_parser.py      # Parse "3000-7000" → min/max (~35 lines)
│   │   ├── currency_converter.py # (~40 lines)
│   │   ├── inflation_adjuster.py # (~35 lines)
│   │   ├── gap_interpolator.py  # (~40 lines)
│   │   ├── deduplicator.py      # (~30 lines)
│   │   └── outlier_flagger.py   # (~35 lines)
│   ├── quality/                 # Validation rules
│   │   ├── rules.py             # Individual check functions (~50 lines)
│   │   └── validator.py         # Run all checks (~40 lines)
│   ├── registry.py              # Plugin registry with decorators (~30 lines)
│   └── chain.py                 # TransformChain executor (~25 lines)
│
├── collectors/                  # Inbound adapters — one file per source
│   ├── worldbank.py             # @register_collector (~60 lines)
│   ├── faostat.py               # @register_collector (~70 lines)
│   ├── hcp.py                   # @register_collector (~70 lines)
│   ├── wfp.py                   # @register_collector (~50 lines)
│   ├── news_scraper.py          # @register_collector (~80 lines)
│   ├── selina.py                # @register_collector (~50 lines)
│   └── manual.py                # @register_collector (~30 lines)
│
├── adapters/                    # I/O adapters
│   ├── kafka/
│   │   ├── producer.py          # Publish to Kafka (~40 lines)
│   │   ├── consumer.py          # Consume from Kafka (~40 lines)
│   │   └── avro_serde.py        # Avro serialization (~35 lines)
│   ├── spark/
│   │   ├── session.py           # SparkSession factory (~25 lines)
│   │   ├── bronze_writer.py     # Kafka → Delta bronze (~40 lines)
│   │   ├── bronze_to_silver.py  # Apply transform chain (~50 lines)
│   │   ├── silver_to_gold.py    # Build star schema (~60 lines)
│   │   └── gold_to_postgres.py  # Materialize to PG (~40 lines)
│   ├── storage/
│   │   ├── delta.py             # Delta Lake adapter (~40 lines)
│   │   └── postgres.py          # PostgreSQL adapter (~50 lines)
│   └── http/
│       ├── api_client.py        # Shared HTTP client (~35 lines)
│       └── scraper.py           # Shared scraping utils (~40 lines)
│
├── api/                         # Outbound adapter — FastAPI
│   ├── app.py                   # App factory (~20 lines)
│   ├── deps.py                  # Dependency injection (~20 lines)
│   └── routes/
│       ├── prices.py            # GET /prices (~50 lines)
│       ├── products.py          # GET /products (~30 lines)
│       ├── trends.py            # GET /trends (~30 lines)
│       ├── sources.py           # GET /sources (~25 lines)
│       ├── quality.py           # GET /quality (~25 lines)
│       └── export.py            # GET /export (~35 lines)
│
├── publishing/                  # Outbound adapters
│   ├── github_release.py        # (~40 lines)
│   └── kaggle_push.py           # (~35 lines)
│
├── logging/
│   └── setup.py                 # structlog config (~30 lines)
│
└── config.py                    # pydantic-settings (~35 lines)
```

---

## Size Limits (Hard Rules)

| Element | Hard Max | Target | If exceeded |
|---------|---------|--------|-------------|
| **File / Module** | **100 lines** | 60-80 | Split into focused files |
| **Function** | **15 lines** | 5-10 | Extract helper |
| **Class** | **80 lines** | 50 | Split responsibility |
| **Class methods** | **8 methods** | 5-6 | Split into two classes |
| **Nesting depth** | **2 levels** | 1 | Guard clauses, extract fn |
| **Parameters** | **3 params** | 2 | Use config/dataclass |
| **Line length** | **88 chars** | — | ruff enforces |

---

## Clean Code Rules

### Naming
- Names reveal intent. No abbreviations except `url`, `id`, `cpi`, `db`.
- Classes = **nouns**: `PriceNormalizer`, `WorldBankCollector`
- Functions = **verbs**: `normalize_unit()`, `fetch_prices()`
- Booleans = **questions**: `is_subsidized`, `has_variety`
- No generics: no `data`, `info`, `temp`, `result`, `item`, `obj`
- Domain language: `observation` not `record`, `collector` not `fetcher`

### Functions
- One thing per function. Period.
- Return early with guard clauses. Happy path unindented.
- No flag arguments. No booleans that switch behavior.
- `get_X` must not modify state. `update_X` says it modifies.

```python
# BAD — if hell
def process(obs):
    if obs is not None:
        if obs.price is not None:
            if obs.price > 0:
                ...

# GOOD — guard clauses
def process(obs: Observation) -> CleanPrice:
    if obs is None:
        raise InvalidObservation("null observation")
    if not obs.has_valid_price():
        return CleanPrice.empty("invalid_price")
    return normalize(obs)
```

### No If Hell
- **2 nesting levels max.** Period.
- Guard clauses for early returns.
- Registry pattern for source dispatch (not if/elif).
- Dict dispatch for mappings (not if/elif).
- Polymorphism for type-based behavior (not isinstance chains).
- TransformChain for sequential logic (not cascading ifs).

### Comments
- Code is self-documenting. Comments explain **why**, never **what**.
- One-line docstring per module.
- Docstrings on public functions: args, returns, raises.
- No commented-out code. Git remembers.
- No TODO without issue number: `# TODO(#42): handle base year switch`

### Error Handling
- Custom exceptions with context. No bare `Exception`.
- Fail fast. No silent swallowing.

```python
class MaPrixError(Exception): ...
class CollectorError(MaPrixError): ...
class SourceUnavailable(CollectorError): ...
class SchemaViolation(MaPrixError): ...
class UnsupportedConversion(MaPrixError): ...
```

---

## Extensibility (Open/Closed)

### Adding a new data source
1. Create `src/collectors/new_source.py` (~60 lines)
2. Decorate with `@register_collector("new_source")`
3. Add Avro schema in `config/kafka/schemas/`
4. Add Airflow DAG in `config/airflow/dags/`
5. **No existing code changes.**

### Adding a new transformer
1. Create `src/core/transformers/new_step.py` (~40 lines)
2. Implement `BaseTransformer`
3. Add to chain config
4. **No existing code changes.**

### Adding a new product
1. Add rows to `data/seeds/products.csv`
2. Run seed loader
3. **No code changes.**

---

## Python Conventions

### Style
- **Formatter**: `ruff format`
- **Linter**: `ruff check`
- **Types**: `mypy --strict`. All functions have type hints.
- **Quotes**: double `"like this"`
- **Imports**: sorted by ruff, no `*` imports

### Patterns
- `dataclass(frozen=True)` for domain models (immutable)
- `pydantic.BaseModel` for API schemas and config
- `ABC` + `@abstractmethod` for ports
- `Enum` for fixed value sets
- `pathlib.Path` not string paths
- `structlog` not `print()`
- Context managers for resources
- Generators for large data

### Testing
- `pytest` + `hypothesis` (property-based) + `chispa` (Spark)
- Coverage: 80%+ on core domain
- Test mirrors source: `src/collectors/worldbank.py` → `tests/collectors/test_worldbank.py`
- Test names describe behavior: `test_converts_tonne_to_kg`
- Core tests = zero mocks. Adapter tests = mock external I/O.

---

## Banned

- Global mutable state
- `*` imports
- Bare `except`
- Magic numbers (use named constants)
- String SQL concatenation (use parameterized)
- `print()` (use structlog)
- Hardcoded URLs/paths (use config)
- Commented-out code
- Dead code
- Copy-paste (extract a function)
- Nested ternaries
- God classes
- Flag arguments
