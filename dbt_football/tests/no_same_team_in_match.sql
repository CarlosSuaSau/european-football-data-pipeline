SELECT *
FROM {{ ref('stg_matches') }}

WHERE home_team_id = away_team_id