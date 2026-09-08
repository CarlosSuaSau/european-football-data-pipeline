SELECT
    season_id,
    team_id

FROM {{ source('football_v1', 'season_teams') }}