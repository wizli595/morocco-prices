"""Create bronze layer Delta tables (one per source)."""

from pyspark.sql import SparkSession

BRONZE_PATH = "/data/bronze"
SOURCES = ["worldbank", "faostat", "hcp", "wfp", "news", "manual"]


def create_bronze_tables(spark: SparkSession) -> int:
    """Create empty bronze Delta tables, return count."""
    for src in SOURCES:
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS bronze_{src} (
                raw_json STRING,
                source STRING,
                ingested_at TIMESTAMP,
                pipeline_run_id STRING
            ) USING DELTA LOCATION '{BRONZE_PATH}/{src}'
        """)
    return len(SOURCES)


if __name__ == "__main__":
    from scripts.spark_session import get_spark

    spark = get_spark()
    spark.sql("CREATE DATABASE IF NOT EXISTS maprix")
    spark.sql("USE maprix")
    n = create_bronze_tables(spark)
    print(f"Bronze tables: {n}")
    spark.stop()
