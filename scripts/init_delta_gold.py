"""Create gold layer Delta table (star schema fact)."""

from pyspark.sql import SparkSession

GOLD_PATH = "/data/gold"


def create_gold_table(spark: SparkSession) -> None:
    """Create the gold_fact_prices Delta table."""
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS gold_fact_prices (
            observation_id STRING,
            product_key INT,
            location_key INT,
            time_key INT,
            source_key INT,
            price_mad DOUBLE,
            price_usd DOUBLE,
            price_real_mad DOUBLE,
            confidence STRING,
            pipeline_run_id STRING
        ) USING DELTA
        PARTITIONED BY (time_key)
        LOCATION '{GOLD_PATH}/fact_prices'
    """)


if __name__ == "__main__":
    from scripts.spark_session import get_spark

    spark = get_spark()
    spark.sql("USE maprix")
    create_gold_table(spark)
    print("Gold table: gold_fact_prices")
    spark.stop()
