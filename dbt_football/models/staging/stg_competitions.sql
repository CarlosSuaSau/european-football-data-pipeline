SELECT
    id AS competition_id,
    code AS competition_code,
    name AS competition_name

FROM {{ source('football_v1', 'competitions') }}