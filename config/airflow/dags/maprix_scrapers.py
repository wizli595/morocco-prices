"""MaPrix scrapers: refresh current retail/market prices weekly."""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def _scrape() -> None:
    from scripts.run_scrapers import run

    run()


def _verify() -> None:
    from scripts.verify_data import run

    run()


def _process() -> None:
    from scripts.run_processing import run

    run()


with DAG(
    dag_id="maprix_scrapers",
    description="Scrape current retail/market prices, verify, and enrich",
    schedule="@weekly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["maprix", "scrapers"],
) as dag:
    scrape = PythonOperator(task_id="scrape", python_callable=_scrape)
    verify = PythonOperator(task_id="verify", python_callable=_verify)
    process = PythonOperator(task_id="process", python_callable=_process)

    scrape >> verify >> process
