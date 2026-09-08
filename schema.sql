CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL
);


CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY,
    competition_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    current_matchday INTEGER,

    CONSTRAINT fk_season_competition
        FOREIGN KEY (competition_id)
        REFERENCES competitions(id),

    CONSTRAINT unique_competition_season
        UNIQUE (competition_id, start_date, end_date),

    CONSTRAINT valid_season_dates
        CHECK (end_date >= start_date),

    CONSTRAINT valid_current_matchday
        CHECK (current_matchday IS NULL OR current_matchday > 0)
);


CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    short_name VARCHAR(100),
    tla VARCHAR(10),
    crest_url TEXT
);


CREATE TABLE IF NOT EXISTS season_teams (
    season_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,

    PRIMARY KEY (season_id, team_id),

    CONSTRAINT fk_season_team_season
        FOREIGN KEY (season_id)
        REFERENCES seasons(id),

    CONSTRAINT fk_season_team_team
        FOREIGN KEY (team_id)
        REFERENCES teams(id)
);


CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    season_id INTEGER NOT NULL,
    utc_date TIMESTAMPTZ NOT NULL,
    matchday INTEGER,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL,
    home_goals INTEGER,
    away_goals INTEGER,
    winner VARCHAR(20),

    CONSTRAINT fk_match_season
        FOREIGN KEY (season_id)
        REFERENCES seasons(id),

    CONSTRAINT fk_match_home_team
        FOREIGN KEY (home_team_id)
        REFERENCES teams(id),

    CONSTRAINT fk_match_away_team
        FOREIGN KEY (away_team_id)
        REFERENCES teams(id),

    CONSTRAINT different_teams
        CHECK (home_team_id <> away_team_id),

    CONSTRAINT valid_matchday
        CHECK (matchday IS NULL OR matchday > 0),

    CONSTRAINT valid_home_goals
        CHECK (home_goals IS NULL OR home_goals >= 0),

    CONSTRAINT valid_away_goals
        CHECK (away_goals IS NULL OR away_goals >= 0),

    CONSTRAINT valid_winner
        CHECK (
            winner IS NULL
            OR winner IN ('HOME_TEAM', 'AWAY_TEAM', 'DRAW')
        )
);


CREATE INDEX IF NOT EXISTS idx_matches_season
    ON matches(season_id);

CREATE INDEX IF NOT EXISTS idx_matches_date
    ON matches(utc_date);

CREATE INDEX IF NOT EXISTS idx_matches_home_team
    ON matches(home_team_id);

CREATE INDEX IF NOT EXISTS idx_matches_away_team
    ON matches(away_team_id);