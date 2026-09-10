from datetime import timedelta
import subprocess

import pendulum

from airflow.sdk import dag, task


DBT_PROJECT_DIR = "/opt/airflow/project/dbt_football"


@dag(
    dag_id="football_data_pipeline",
    schedule="0 6 * * *",
    start_date=pendulum.datetime(
        2026,
        9,
        9,
        tz="Europe/Madrid",
    ),
    catchup=False,
    tags=["football", "etl", "dbt"],
)
def football_data_pipeline():

    @task(
        retries=2,
        retry_delay=timedelta(minutes=5),
    )
    def ingest_football_data():
        from main import main

        main()

    @task(
        retries=1,
        retry_delay=timedelta(minutes=2),
    )
    def dbt_run():
        subprocess.run(
            [
                "dbt",
                "run",
                "--project-dir",
                DBT_PROJECT_DIR,
                "--profiles-dir",
                DBT_PROJECT_DIR,
                "--target",
                "docker",
            ],
            check=True,
        )

    @task
    def dbt_test():
        subprocess.run(
            [
                "dbt",
                "test",
                "--project-dir",
                DBT_PROJECT_DIR,
                "--profiles-dir",
                DBT_PROJECT_DIR,
                "--target",
                "docker",
            ],
            check=True,
        )

    ingestion = ingest_football_data()
    models = dbt_run()
    tests = dbt_test()

    ingestion >> models >> tests


football_data_pipeline()