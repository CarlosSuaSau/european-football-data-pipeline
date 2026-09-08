import os
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """Create and return a PostgreSQL connection."""

    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )

    except psycopg2.Error as exc:
        raise RuntimeError(
            f"Could not connect to PostgreSQL: {exc}"
        ) from exc


def initialize_database():
    """Create the database tables defined in schema.sql."""

    schema_path = Path(__file__).with_name("schema.sql")

    try:
        sql = schema_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(
            f"Could not read schema.sql: {exc}"
        ) from exc

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)

    except psycopg2.Error as exc:
        raise RuntimeError(
            f"Could not initialize database: {exc}"
        ) from exc


def upsert_competition(cursor, competition):
    sql = """
        INSERT INTO competitions (
            id,
            code,
            name
        )
        VALUES (%s, %s, %s)

        ON CONFLICT (id)
        DO UPDATE SET
            code = EXCLUDED.code,
            name = EXCLUDED.name;
    """

    cursor.execute(
        sql,
        (
            competition["id"],
            competition["code"],
            competition["name"],
        ),
    )


def upsert_season(cursor, season):
    sql = """
        INSERT INTO seasons (
            id,
            competition_id,
            start_date,
            end_date,
            current_matchday
        )
        VALUES (%s, %s, %s, %s, %s)

        ON CONFLICT (id)
        DO UPDATE SET
            competition_id = EXCLUDED.competition_id,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date,
            current_matchday = EXCLUDED.current_matchday;
    """

    cursor.execute(
        sql,
        (
            season["id"],
            season["competition_id"],
            season["start_date"],
            season["end_date"],
            season["current_matchday"],
        ),
    )


def upsert_teams(cursor, teams):
    if not teams:
        return

    sql = """
        INSERT INTO teams (
            id,
            name,
            short_name,
            tla,
            crest_url
        )
        VALUES (%s, %s, %s, %s, %s)

        ON CONFLICT (id)
        DO UPDATE SET
            name = EXCLUDED.name,
            short_name = EXCLUDED.short_name,
            tla = EXCLUDED.tla,
            crest_url = EXCLUDED.crest_url;
    """

    values = [
        (
            team["id"],
            team["name"],
            team["short_name"],
            team["tla"],
            team["crest_url"],
        )
        for team in teams
    ]

    execute_batch(cursor, sql, values)


def upsert_season_teams(cursor, season_teams):
    if not season_teams:
        return

    sql = """
        INSERT INTO season_teams (
            season_id,
            team_id
        )
        VALUES (%s, %s)

        ON CONFLICT (season_id, team_id)
        DO NOTHING;
    """

    values = [
        (
            relation["season_id"],
            relation["team_id"],
        )
        for relation in season_teams
    ]

    execute_batch(cursor, sql, values)


def upsert_matches(cursor, matches):
    if not matches:
        return

    sql = """
        INSERT INTO matches (
            id,
            season_id,
            utc_date,
            matchday,
            home_team_id,
            away_team_id,
            status,
            home_goals,
            away_goals,
            winner
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (id)
        DO UPDATE SET
            season_id = EXCLUDED.season_id,
            utc_date = EXCLUDED.utc_date,
            matchday = EXCLUDED.matchday,
            home_team_id = EXCLUDED.home_team_id,
            away_team_id = EXCLUDED.away_team_id,
            status = EXCLUDED.status,
            home_goals = EXCLUDED.home_goals,
            away_goals = EXCLUDED.away_goals,
            winner = EXCLUDED.winner;
    """

    values = [
        (
            match["id"],
            match["season_id"],
            match["utc_date"],
            match["matchday"],
            match["home_team_id"],
            match["away_team_id"],
            match["status"],
            match["home_goals"],
            match["away_goals"],
            match["winner"],
        )
        for match in matches
    ]

    execute_batch(cursor, sql, values)


def save_competition_data(
    competition,
    season,
    teams,
    season_teams,
    matches,
):
    """
    Store all data for one competition in a single transaction.
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                upsert_competition(cursor, competition)
                upsert_season(cursor, season)
                upsert_teams(cursor, teams)
                upsert_season_teams(cursor, season_teams)
                upsert_matches(cursor, matches)

    except psycopg2.Error as exc:
        raise RuntimeError(
            f"Could not save competition data: {exc}"
        ) from exc