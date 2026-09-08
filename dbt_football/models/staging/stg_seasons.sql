SELECT
    id AS season_id,
    competition_id,
    start_date,
    end_date,
    current_matchday

FROM {{ source('football_v1', 'seasons') }}