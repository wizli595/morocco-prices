FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi>=0.110 \
    uvicorn>=0.29 \
    pydantic>=2.7 \
    pydantic-settings>=2.2 \
    structlog>=24.1 \
    psycopg2-binary>=2.9 \
    sqlalchemy>=2.0 \
    prometheus-client>=0.20 \
    python-dotenv>=1.0 \
    httpx>=0.27

COPY src/ src/
COPY data/seeds/ data/seeds/
COPY data/manual/ data/manual/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.app:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
