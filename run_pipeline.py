import logging
import subprocess
from pathlib import Path

from main import main as run_ingestion


logger = logging.getLogger(__name__)

DBT_PROJECT_DIR = Path(__file__).parent / "dbt_football"


def run_dbt(command):
    logger.info("Running dbt %s...", command)

    subprocess.run(
        [
            "dbt",
            command,
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--profiles-dir",
            str(DBT_PROJECT_DIR),
            "--target",
            "prod",
        ],
        check=True,
    )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
    )

    logger.info("Starting production football pipeline.")

    run_ingestion()
    run_dbt("run")
    run_dbt("test")

    logger.info("Production football pipeline completed successfully.")


if __name__ == "__main__":
    main()