WITH matches AS (

    SELECT *
    FROM {{ ref('fct_matches') }}
    WHERE status = 'FINISHED'

),

home_team AS (

    SELECT
        match_id,
        competition_id,
        competition_code,
        competition_name,
        season_id,
        season,
        matchday,
        match_date,

        home_team_id AS team_id,
        home_team AS team_name,

        away_team_id AS opponent_id,
        away_team AS opponent_name,

        'HOME' AS venue,

        home_goals AS goals_for,
        away_goals AS goals_against,

        home_goals - away_goals AS goal_difference,

        CASE
            WHEN result = 'HOME_WIN' THEN 'WIN'
            WHEN result = 'DRAW' THEN 'DRAW'
            ELSE 'LOSS'
        END AS result,

        home_points AS points,

        CASE WHEN result = 'HOME_WIN' THEN 1 ELSE 0 END AS win,
        CASE WHEN result = 'DRAW' THEN 1 ELSE 0 END AS draw,
        CASE WHEN result = 'AWAY_WIN' THEN 1 ELSE 0 END AS loss

    FROM matches

),

away_team AS (

    SELECT
        match_id,
        competition_id,
        competition_code,
        competition_name,
        season_id,
        season,
        matchday,
        match_date,

        away_team_id AS team_id,
        away_team AS team_name,

        home_team_id AS opponent_id,
        home_team AS opponent_name,

        'AWAY' AS venue,

        away_goals AS goals_for,
        home_goals AS goals_against,

        away_goals - home_goals AS goal_difference,

        CASE
            WHEN result = 'AWAY_WIN' THEN 'WIN'
            WHEN result = 'DRAW' THEN 'DRAW'
            ELSE 'LOSS'
        END AS result,

        away_points AS points,

        CASE WHEN result = 'AWAY_WIN' THEN 1 ELSE 0 END AS win,
        CASE WHEN result = 'DRAW' THEN 1 ELSE 0 END AS draw,
        CASE WHEN result = 'HOME_WIN' THEN 1 ELSE 0 END AS loss

    FROM matches

)

SELECT *
FROM home_team

UNION ALL

SELECT *
FROM away_team