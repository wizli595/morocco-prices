"""Shared Spark session factory for init scripts."""

from pyspark.sql import SparkSession


def get_spark() -> SparkSession:
    """Create Spark session with Delta Lake + Hive support."""
    return (
        SparkSession.builder.appName("maprix-init")
        .config(
            "spark.sql.extensions",
            "io.delta.sql.DeltaSparkSessionExtension",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .enableHiveSupport()
        .getOrCreate()
    )
