WITH moon AS (
    SELECT DISTINCT CAST(full_moon_date AS DATE) AS d
    FROM {{ ref('seed_full_moon_dates') }}
),
reviews_flag AS (
    SELECT
        r.review_date,
        (moon.d IS NOT NULL) AS is_full_moon,
        CASE WHEN r.sentiment = 'positive' THEN 1.0 ELSE 0.0 END AS is_positive
    FROM {{ ref('sl_reviews') }} r
    LEFT JOIN moon ON r.review_date = moon.d
)
SELECT
    CASE WHEN is_full_moon THEN 'Pleine lune' ELSE 'Nuit normale' END AS periode,
    COUNT(*)                                  AS nb_reviews,
    COUNT(DISTINCT review_date)               AS nb_nuits,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT review_date), 1) AS avis_par_nuit,
    ROUND(AVG(is_positive) * 100, 1)          AS pct_positif
FROM reviews_flag
GROUP BY 1
