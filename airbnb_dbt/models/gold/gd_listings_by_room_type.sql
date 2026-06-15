SELECT
    room_type,
    COUNT(*)        AS nb_listings,
    ROUND(AVG(price), 2) AS avg_price
FROM {{ ref('sl_listings') }}
GROUP BY room_type
ORDER BY nb_listings DESC
