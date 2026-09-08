from datetime import date, datetime


def parse_date(value):
    """Convert an API date string into a Python date."""
    if value is None:
        return None

    return date.fromisoformat(value)


def parse_datetime(value):
    """Convert an API UTC datetime string into a Python datetime."""
    if value is None:
        return None

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def transform_competition(data):
    """Extract the competition fields required by our database."""

    try:
        return {
            "id": data["id"],
            "code": data["code"],
            "name": data["name"],
        }
    except KeyError as exc:
        raise ValueError(
            f"Unexpected competition data: missing field {exc}"
        ) from exc


def transform_season(data):
    """Extract the current season from a competition response."""

    try:
        season = data["currentSeason"]

        return {
            "id": season["id"],
            "competition_id": data["id"],
            "start_date": parse_date(season["startDate"]),
            "end_date": parse_date(season["endDate"]),
            "current_matchday": season.get("currentMatchday"),
        }

    except KeyError as exc:
        raise ValueError(
            f"Unexpected season data: missing field {exc}"
        ) from exc


def transform_teams(data):
    """Transform the list of teams returned by the API."""

    if "teams" not in data or not isinstance(data["teams"], list):
        raise ValueError("Unexpected teams response.")

    teams = []

    for team in data["teams"]:
        try:
            transformed_team = {
                "id": team["id"],
                "name": team["name"],
                "short_name": team.get("shortName"),
                "tla": team.get("tla"),
                "crest_url": team.get("crest"),
            }

        except KeyError as exc:
            raise ValueError(
                f"Unexpected team data: missing field {exc}"
            ) from exc

        teams.append(transformed_team)

    return teams


def transform_season_teams(teams, season_id):
    """
    Create the relationships between a season and
    the teams participating in it.
    """

    return [
        {
            "season_id": season_id,
            "team_id": team["id"],
        }
        for team in teams
    ]


def transform_matches(data):
    """Transform the matches returned by the API."""

    if "matches" not in data or not isinstance(data["matches"], list):
        raise ValueError("Unexpected matches response.")

    matches = []

    for match in data["matches"]:
        try:
            score = match.get("score") or {}
            full_time = score.get("fullTime") or {}

            transformed_match = {
                "id": match["id"],
                "season_id": match["season"]["id"],
                "utc_date": parse_datetime(match["utcDate"]),
                "matchday": match.get("matchday"),
                "home_team_id": match["homeTeam"]["id"],
                "away_team_id": match["awayTeam"]["id"],
                "status": match["status"],
                "home_goals": full_time.get("home"),
                "away_goals": full_time.get("away"),
                "winner": score.get("winner"),
            }

        except KeyError as exc:
            raise ValueError(
                f"Unexpected match data: missing field {exc}"
            ) from exc

        matches.append(transformed_match)

    return matches