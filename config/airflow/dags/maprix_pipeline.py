"""MaPrix end-to-end pipeline: collect -> verify -> clean -> export."""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def _collect() -> None:
    from scripts.run_collectors import run_all

    run_all()


def _verify() -> None:
    from scripts.verify_data import run

    run()


def _process() -> None:
    from scripts.run_processing import run

    run()


def _export() -> None:
    from scripts.export_dataset import run

    run()


with DAG(
    dag_id="maprix_pipeline",
    description="Collect, verify, clean, and export Morocco price data",
    schedule="@monthly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["maprix"],
) as dag:
    collect = PythonOperator(task_id="collect", python_callable=_collect)
    verify = PythonOperator(task_id="verify", python_callable=_verify)
    process = PythonOperator(task_id="process", python_callable=_process)
    export = PythonOperator(task_id="export", python_callable=_export)

    collect >> verify >> process >> export
