SELECT
    id AS team_id,
    name AS team_name,
    short_name,
    tla,
    crest_url

FROM {{ source('football_v1', 'teams') }}