import os
import time

import requests
from dotenv import load_dotenv


BASE_URL = "https://api.football-data.org/v4"

COMPETITIONS = {
    "LaLiga": "PD",
    "Premier League": "PL",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "Ligue 1": "FL1",
}

TIMEOUT = 15
MAX_RETRIES = 3


load_dotenv()


def get_headers():
    """Build the headers required to authenticate with the API."""
    token = os.getenv("FOOTBALL_DATA_API_TOKEN")

    if not token:
        raise RuntimeError(
            "FOOTBALL_DATA_API_TOKEN is not defined in the environment."
        )

    return {
        "X-Auth-Token": token
    }


def make_request(endpoint, params=None):
    """
    Perform a GET request to football-data.org
    and return the response as a Python dictionary.
    """

    url = f"{BASE_URL}{endpoint}"

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                url,
                headers=get_headers(),
                params=params,
                timeout=TIMEOUT,
            )

        except requests.RequestException as exc:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(
                    f"Could not connect to football-data.org: {exc}"
                ) from exc

            time.sleep(2 ** attempt)
            continue

        # API request limit reached
        if response.status_code == 429:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError("API request limit exceeded.")

            reset_seconds = response.headers.get(
                "X-RequestCounter-Reset",
                "10"
            )

            try:
                wait_time = int(reset_seconds) + 1
            except ValueError:
                wait_time = 10

            time.sleep(wait_time)
            continue

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(
                f"API error {response.status_code}: {response.text}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "The API returned an invalid JSON response."
            ) from exc

        if not isinstance(data, dict):
            raise RuntimeError("Unexpected API response format.")

        return data

    raise RuntimeError("Request failed after several attempts.")


def get_competition(competition_code):
    """Get general information about a competition."""
    return make_request(f"/competitions/{competition_code}")


def get_teams(competition_code):
    """Get teams participating in the current season."""
    return make_request(f"/competitions/{competition_code}/teams")


def get_matches(competition_code):
    """Get matches from the current season."""
    return make_request(f"/competitions/{competition_code}/matches")