WITH matches AS (

    SELECT *
    FROM {{ ref('stg_matches') }}

),

seasons AS (

    SELECT *
    FROM {{ ref('stg_seasons') }}

),

competitions AS (

    SELECT *
    FROM {{ ref('stg_competitions') }}

),

teams AS (

    SELECT *
    FROM {{ ref('stg_teams') }}

)

SELECT
    m.match_id,

    c.competition_id,
    c.competition_code,
    c.competition_name,

    s.season_id,

    TO_CHAR(s.start_date, 'YYYY')
        || '/'
        || RIGHT(TO_CHAR(s.end_date, 'YYYY'), 2)
        AS season,

    m.matchday,
    m.match_datetime_utc,

    (m.match_datetime_utc AT TIME ZONE 'UTC')::DATE
        AS match_date,

    home.team_id AS home_team_id,
    home.team_name AS home_team,

    away.team_id AS away_team_id,
    away.team_name AS away_team,

    m.status,

    m.home_goals,
    m.away_goals,

    m.winner AS winner_code,

    CASE
        WHEN m.status <> 'FINISHED' THEN NULL
        WHEN m.winner = 'HOME_TEAM' THEN home.team_name
        WHEN m.winner = 'AWAY_TEAM' THEN away.team_name
        ELSE NULL
    END AS winner_team,

    CASE
        WHEN m.status <> 'FINISHED' THEN NULL
        WHEN m.winner = 'HOME_TEAM' THEN 'HOME_WIN'
        WHEN m.winner = 'AWAY_TEAM' THEN 'AWAY_WIN'
        WHEN m.winner = 'DRAW' THEN 'DRAW'
    END AS result,

    CASE
        WHEN m.status = 'FINISHED'
        THEN m.home_goals + m.away_goals
    END AS total_goals,

    CASE
        WHEN m.status = 'FINISHED'
        THEN m.home_goals - m.away_goals
    END AS goal_difference,

    CASE
        WHEN m.status = 'FINISHED'
        THEN m.winner = 'DRAW'
    END AS is_draw,

    CASE
        WHEN m.status <> 'FINISHED' THEN NULL
        WHEN m.winner = 'HOME_TEAM' THEN 3
        WHEN m.winner = 'DRAW' THEN 1
        ELSE 0
    END AS home_points,

    CASE
        WHEN m.status <> 'FINISHED' THEN NULL
        WHEN m.winner = 'AWAY_TEAM' THEN 3
        WHEN m.winner = 'DRAW' THEN 1
        ELSE 0
    END AS away_points

FROM matches m

JOIN seasons s
    ON m.season_id = s.season_id

JOIN competitions c
    ON s.competition_id = c.competition_id

JOIN teams home
    ON m.home_team_id = home.team_id

JOIN teams away
    ON m.away_team_id = away.team_id