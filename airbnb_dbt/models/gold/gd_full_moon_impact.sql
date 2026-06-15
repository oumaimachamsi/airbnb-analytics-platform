WITH moon AS (
    SELECT CAST(full_moon_date AS DATE) AS d
    FROM {{ ref('seed_full_moon_dates') }}
)
SELECT
    CASE WHEN moon.d IS NOT NULL THEN 'Pleine lune' ELSE 'Nuit normale' END AS periode,
    COUNT(*)            AS nb_reviews,
    ROUND(AVG(CASE WHEN r.sentiment = 'positive' THEN 1.0 ELSE 0.0 END), 3) AS taux_positif
FROM {{ ref('sl_reviews') }} r
LEFT JOIN moon ON r.review_date = moon.d
GROUP BY 1
