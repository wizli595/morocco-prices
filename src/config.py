"""Application settings loaded from environment."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration, loaded from .env."""

    model_config = {"env_file": ".env", "extra": "ignore"}

    # Project
    project_name: str = "maprix"
    environment: str = "development"

    # PostgreSQL (host-side default; containers override to 5432 internally)
    postgres_host: str = "localhost"
    postgres_port: int = 5434
    postgres_user: str = "maprix"
    postgres_password: str = "changeme"
    postgres_db: str = "maprix"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_schema_registry_url: str = "http://localhost:8081"

    # Spark
    spark_master_url: str = "local[*]"

    # Delta Lake paths
    delta_bronze_path: str = "./data/bronze"
    delta_silver_path: str = "./data/silver"
    delta_gold_path: str = "./data/gold"

    # Collectors
    collector_user_agent: str = "MaPrix/1.0"
    collector_timeout_seconds: int = 30
    collector_max_retries: int = 3

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    @property
    def postgres_url(self) -> str:
        """SQLAlchemy connection string."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
