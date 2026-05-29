"""Create silver layer Delta table (unified schema)."""

from pyspark.sql import SparkSession

SILVER_PATH = "/data/silver"


def create_silver_table(spark: SparkSession) -> None:
    """Create the unified silver_prices Delta table."""
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS silver_prices (
            observation_id STRING,
            product_id STRING,
            location_id STRING,
            time_key INT,
            source_id STRING,
            price_type_id STRING,
            original_value DOUBLE,
            original_min DOUBLE,
            original_max DOUBLE,
            original_unit STRING,
            original_currency STRING,
            price_mad DOUBLE,
            price_usd DOUBLE,
            confidence STRING,
            precision STRING,
            collection_method STRING,
            pipeline_run_id STRING,
            processed_at TIMESTAMP
        ) USING DELTA
        PARTITIONED BY (source_id)
        LOCATION '{SILVER_PATH}/prices'
    """)


if __name__ == "__main__":
    from scripts.spark_session import get_spark

    spark = get_spark()
    spark.sql("USE maprix")
    create_silver_table(spark)
    print("Silver table: silver_prices")
    spark.stop()
