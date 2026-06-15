SELECT
    date_trunc('month', review_date) AS month,
    COUNT(*)                         AS nb_reviews
FROM {{ ref('sl_reviews') }}
GROUP BY 1
ORDER BY 1
