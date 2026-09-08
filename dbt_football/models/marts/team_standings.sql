WITH participants AS (

    SELECT
        st.season_id,
        s.competition_id,
        c.competition_code,
        c.competition_name,

        TO_CHAR(s.start_date, 'YYYY')
            || '/'
            || RIGHT(TO_CHAR(s.end_date, 'YYYY'), 2)
            AS season,

        st.team_id,
        t.team_name

    FROM {{ ref('stg_season_teams') }} st

    JOIN {{ ref('stg_seasons') }} s
        ON st.season_id = s.season_id

    JOIN {{ ref('stg_competitions') }} c
        ON s.competition_id = c.competition_id

    JOIN {{ ref('stg_teams') }} t
        ON st.team_id = t.team_id

),

results AS (

    SELECT
        season_id,
        team_id,

        COUNT(*) AS played,

        SUM(win) AS wins,
        SUM(draw) AS draws,
        SUM(loss) AS losses,

        SUM(goals_for) AS goals_for,
        SUM(goals_against) AS goals_against,
        SUM(goal_difference) AS goal_difference,

        SUM(points) AS points,

        SUM(CASE WHEN venue = 'HOME' THEN 1 ELSE 0 END)
            AS home_played,

        SUM(CASE WHEN venue = 'HOME' THEN win ELSE 0 END)
            AS home_wins,

        SUM(CASE WHEN venue = 'HOME' THEN points ELSE 0 END)
            AS home_points,

        SUM(CASE WHEN venue = 'AWAY' THEN 1 ELSE 0 END)
            AS away_played,

        SUM(CASE WHEN venue = 'AWAY' THEN win ELSE 0 END)
            AS away_wins,

        SUM(CASE WHEN venue = 'AWAY' THEN points ELSE 0 END)
            AS away_points

    FROM {{ ref('team_match_results') }}

    GROUP BY
        season_id,
        team_id

),

standings AS (

    SELECT
        p.competition_id,
        p.competition_code,
        p.competition_name,

        p.season_id,
        p.season,

        p.team_id,
        p.team_name,

        COALESCE(r.played, 0) AS played,
        COALESCE(r.wins, 0) AS wins,
        COALESCE(r.draws, 0) AS draws,
        COALESCE(r.losses, 0) AS losses,

        COALESCE(r.goals_for, 0) AS goals_for,
        COALESCE(r.goals_against, 0) AS goals_against,
        COALESCE(r.goal_difference, 0) AS goal_difference,

        COALESCE(r.points, 0) AS points,

        COALESCE(r.home_played, 0) AS home_played,
        COALESCE(r.home_wins, 0) AS home_wins,
        COALESCE(r.home_points, 0) AS home_points,

        ROUND(
            COALESCE(r.home_points, 0)::NUMERIC
            / NULLIF(COALESCE(r.home_played, 0), 0),
            2
        ) AS home_points_per_match,

        COALESCE(r.away_played, 0) AS away_played,
        COALESCE(r.away_wins, 0) AS away_wins,
        COALESCE(r.away_points, 0) AS away_points,

        ROUND(
            COALESCE(r.away_points, 0)::NUMERIC
            / NULLIF(COALESCE(r.away_played, 0), 0),
            2
        ) AS away_points_per_match

    FROM participants p

    LEFT JOIN results r
        ON p.season_id = r.season_id
        AND p.team_id = r.team_id

)

SELECT
    ROW_NUMBER() OVER (
        PARTITION BY competition_id, season_id

        ORDER BY
            points DESC,
            goal_difference DESC,
            goals_for DESC,
            team_name
    ) AS position,

    *

FROM standings