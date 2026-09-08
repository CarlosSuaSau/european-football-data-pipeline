import logging

from api import (
    COMPETITIONS,
    get_competition,
    get_teams,
    get_matches,
)

from transform import (
    transform_competition,
    transform_season,
    transform_teams,
    transform_season_teams,
    transform_matches,
)

from database import (
    initialize_database,
    save_competition_data,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


def process_competition(name, code):
    """Run the complete pipeline for one competition."""

    logger.info("Processing %s...", name)

    # 1. Extract
    raw_competition = get_competition(code)
    raw_teams = get_teams(code)
    raw_matches = get_matches(code)

    # 2. Transform
    competition = transform_competition(raw_competition)
    season = transform_season(raw_competition)

    teams = transform_teams(raw_teams)

    season_teams = transform_season_teams(
        teams,
        season["id"],
    )

    matches = transform_matches(raw_matches)

    # 3. Load
    save_competition_data(
        competition=competition,
        season=season,
        teams=teams,
        season_teams=season_teams,
        matches=matches,
    )

    logger.info(
        "%s completed: %d teams, %d matches.",
        name,
        len(teams),
        len(matches),
    )


def main():
    logger.info("Initializing database...")
    initialize_database()

    for name, code in COMPETITIONS.items():
        try:
            process_competition(name, code)

        except Exception as exc:
            logger.error(
                "Could not process %s: %s",
                name,
                exc,
            )

    logger.info("Pipeline finished.")


if __name__ == "__main__":
    main()