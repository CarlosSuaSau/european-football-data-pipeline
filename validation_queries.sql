-- Team with the most match victories.
SELECT
    t.name AS team,
    COUNT(*) AS wins
FROM matches m
JOIN teams t
    ON (m.winner = 'HOME_TEAM' AND m.home_team_id = t.id)
    OR (m.winner = 'AWAY_TEAM' AND m.away_team_id = t.id)
WHERE m.status = 'FINISHED'
GROUP BY t.id, t.name
ORDER BY wins DESC
LIMIT 1;



-- Teams with the most goals
SELECT
    t.name AS team,
    ROUND(
        SUM(
            CASE
                WHEN m.home_team_id = t.id THEN m.home_goals
                ELSE m.away_goals
            END
        )::NUMERIC / COUNT(*),
        2
    ) AS goals_per_match
FROM teams t
JOIN matches m
    ON t.id = m.home_team_id
    OR t.id = m.away_team_id
WHERE m.status = 'FINISHED'
GROUP BY t.id, t.name
ORDER BY goals_per_match DESC
LIMIT 10;



-- Competitions ordered by goal AVG
SELECT
    c.name AS competition,
    ROUND(
        AVG(m.home_goals + m.away_goals),
        2
    ) AS average_goals
FROM matches m
JOIN seasons s
    ON m.season_id = s.id
JOIN competitions c
    ON s.competition_id = c.id
WHERE m.status = 'FINISHED'
GROUP BY c.id, c.name
ORDER BY average_goals DESC;



-- Teams ordered by home wins.
SELECT
    t.name AS team,
    COUNT(*) AS home_matches,
    COUNT(*) FILTER (
        WHERE m.winner = 'HOME_TEAM'
    ) AS home_wins,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE m.winner = 'HOME_TEAM'
        ) / COUNT(*),
        2
    ) AS home_win_percentage
FROM matches m
JOIN teams t
    ON m.home_team_id = t.id
WHERE m.status = 'FINISHED'
GROUP BY t.id, t.name
ORDER BY home_win_percentage DESC;



-- Matchdays ordered by total goals
SELECT
    c.name AS competition,
    m.matchday,
    SUM(m.home_goals + m.away_goals) AS total_goals
FROM matches m
JOIN seasons s
    ON m.season_id = s.id
JOIN competitions c
    ON s.competition_id = c.id
WHERE m.status = 'FINISHED'
GROUP BY c.id, c.name, m.matchday
ORDER BY total_goals DESC;



-- Draw percentage per competition
SELECT
    c.name AS competition,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE m.winner = 'DRAW'
        ) / COUNT(*),
        2
    ) AS draw_percentage
FROM matches m
JOIN seasons s
    ON m.season_id = s.id
JOIN competitions c
    ON s.competition_id = c.id
WHERE m.status = 'FINISHED'
GROUP BY c.id, c.name
ORDER BY draw_percentage DESC;



-- Difference between home goals and away goals by competiton
SELECT
    c.name AS competition,
    SUM(m.home_goals) AS home_goals,
    SUM(m.away_goals) AS away_goals,
    SUM(m.home_goals) - SUM(m.away_goals) AS difference
FROM matches m
JOIN seasons s
    ON m.season_id = s.id
JOIN competitions c
    ON s.competition_id = c.id
WHERE m.status = 'FINISHED'
GROUP BY c.id, c.name
ORDER BY difference DESC;