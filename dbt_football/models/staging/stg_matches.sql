SELECT
    id AS match_id,
    season_id,
    utc_date AS match_datetime_utc,
    matchday,
    home_team_id,
    away_team_id,
    status,
    home_goals,
    away_goals,
    winner

FROM {{ source('football_v1', 'matches') }}