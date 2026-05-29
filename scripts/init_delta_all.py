"""Initialize all Delta Lake tables (bronze + silver + gold)."""

from scripts.init_delta_bronze import create_bronze_tables
from scripts.init_delta_gold import create_gold_table
from scripts.init_delta_silver import create_silver_table
from scripts.spark_session import get_spark


def main() -> None:
    """Create all Delta tables and register in Hive."""
    print("Creating Delta Lake tables...")
    spark = get_spark()

    spark.sql("CREATE DATABASE IF NOT EXISTS maprix")
    spark.sql("USE maprix")

    n = create_bronze_tables(spark)
    print(f"  Bronze: {n} tables")

    create_silver_table(spark)
    print("  Silver: silver_prices")

    create_gold_table(spark)
    print("  Gold: gold_fact_prices")

    spark.sql("SHOW TABLES").show(truncate=False)
    spark.stop()
    print("Done.")


if __name__ == "__main__":
    main()
