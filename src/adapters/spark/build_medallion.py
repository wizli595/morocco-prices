"""Build the bronze/silver/gold Delta medallion from the serving warehouse.

Bronze mirrors the collected observations, silver is the cleaned unified
schema, and gold is the star-schema fact — each layer reading the previous
Delta table so the lineage runs through the lakehouse.
"""

from pyspark.sql import DataFrame, SparkSession

JDBC_URL = "jdbc:postgresql://postgres:5432/maprix"
JDBC_PROPS = {
    "user": "maprix",
    "password": "changeme",
    "driver": "org.postgresql.Driver",
}
BRONZE = "/data/bronze/prices"
SILVER = "/data/silver/prices"
GOLD = "/data/gold/fact_prices_delta"

_SOURCE_QUERY = """(
    SELECT f.observation_id, p.product_id, p.category, l.location_id,
           t.year, t.month, f.product_key, f.location_key,
           f.source_key, f.time_key,
           f.original_value, f.original_unit, f.original_currency,
           f.price_mad, f.price_usd, f.price_real_mad,
           f.confidence, f.precision, f.collection_method, s.source_id
    FROM serving.fact_prices f
    JOIN serving.dim_product p ON f.product_key = p.product_key
    JOIN serving.dim_location l ON f.location_key = l.location_key
    JOIN serving.dim_time t ON f.time_key = t.time_key
    JOIN serving.dim_source s ON f.source_key = s.source_key
) AS src"""


def _spark() -> SparkSession:
    return (
        SparkSession.builder.appName("maprix-medallion")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .getOrCreate()
    )


def _write(df: DataFrame, path: str, partition: str) -> int:
    df.write.format("delta").mode("overwrite").partitionBy(partition).save(path)
    return int(df.count())


def build() -> None:
    """Materialize bronze -> silver -> gold Delta tables."""
    spark = _spark()

    bronze = spark.read.jdbc(JDBC_URL, _SOURCE_QUERY, properties=JDBC_PROPS)
    n_bronze = _write(bronze, BRONZE, "source_id")

    silver = (
        spark.read.format("delta")
        .load(BRONZE)
        .select(
            "observation_id",
            "product_id",
            "category",
            "location_id",
            "time_key",
            "year",
            "source_id",
            "product_key",
            "location_key",
            "source_key",
            "original_value",
            "original_unit",
            "original_currency",
            "price_mad",
            "price_usd",
            "price_real_mad",
            "confidence",
            "precision",
            "collection_method",
        )
    )
    n_silver = _write(silver, SILVER, "source_id")

    gold = (
        spark.read.format("delta")
        .load(SILVER)
        .select(
            "observation_id",
            "product_key",
            "location_key",
            "time_key",
            "source_key",
            "category",
            "year",
            "price_mad",
            "price_usd",
            "price_real_mad",
            "confidence",
        )
    )
    n_gold = _write(gold, GOLD, "year")

    print(f"medallion built | bronze={n_bronze} silver={n_silver} gold={n_gold}")
    spark.stop()


if __name__ == "__main__":
    build()
