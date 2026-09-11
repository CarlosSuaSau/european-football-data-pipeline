import logging
import time

from api import (
    COMPETITIONS,
    get_competition,
    get_teams,
    get_matches,
    get_match,
)

from transform import (
    InvalidMatchStatusError,
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

STATUS_REFRESH_RETRIES = 2
STATUS_REFRESH_DELAY = 2


def transform_matches_with_refresh(raw_matches):
    """
    Transform matches and retry individual matches when the API
    temporarily returns an invalid match status.

    Matches that remain invalid after all refresh attempts are skipped
    instead of preventing the rest of the competition from being loaded.
    """

    if (
        "matches" not in raw_matches
        or not isinstance(raw_matches["matches"], list)
    ):
        raise ValueError("Unexpected matches response.")

    transformed_matches = []
    skipped_matches = []

    for raw_match in raw_matches["matches"]:
        current_match = raw_match

        for attempt in range(STATUS_REFRESH_RETRIES + 1):
            try:
                transformed = transform_matches(
                    {"matches": [current_match]}
                )

                transformed_matches.extend(transformed)
                break

            except InvalidMatchStatusError as exc:
                if attempt == STATUS_REFRESH_RETRIES:
                    logger.warning(
                        "Skipping match %s because status %r "
                        "is still invalid after %d refresh attempts.",
                        exc.match_id,
                        exc.status,
                        STATUS_REFRESH_RETRIES,
                    )

                    skipped_matches.append(exc.match_id)
                    break

                logger.warning(
                    "Match %s returned invalid status %r. "
                    "Refreshing it from the API "
                    "(attempt %d/%d)...",
                    exc.match_id,
                    exc.status,
                    attempt + 1,
                    STATUS_REFRESH_RETRIES,
                )

                time.sleep(STATUS_REFRESH_DELAY)

                current_match = get_match(exc.match_id)

    if raw_matches["matches"] and not transformed_matches:
        raise RuntimeError(
            "No valid matches could be transformed."
        )

    return transformed_matches, skipped_matches


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

    matches, skipped_matches = transform_matches_with_refresh(
        raw_matches
    )

    # 3. Load
    save_competition_data(
        competition=competition,
        season=season,
        teams=teams,
        season_teams=season_teams,
        matches=matches,
    )

    logger.info(
        "%s completed: %d teams, %d valid matches loaded, "
        "%d matches skipped.",
        name,
        len(teams),
        len(matches),
        len(skipped_matches),
    )

    if skipped_matches:
        logger.warning(
            "%s skipped match IDs: %s",
            name,
            ", ".join(str(match_id) for match_id in skipped_matches),
        )


def main():
    logger.info("Initializing database...")
    initialize_database()

    failed_competitions = []

    for name, code in COMPETITIONS.items():
        try:
            process_competition(name, code)

        except Exception:
            logger.exception(
                "Could not process %s",
                name,
            )

            failed_competitions.append(name)

    if failed_competitions:
        raise RuntimeError(
            "Pipeline failed for: "
            + ", ".join(failed_competitions)
        )

    logger.info("Pipeline finished successfully.")


if __name__ == "__main__":
    main()