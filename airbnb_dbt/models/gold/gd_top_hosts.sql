SELECT
    h.host_id,
    h.host_name,
    h.is_superhost,
    COUNT(l.listing_id) AS nb_listings
FROM {{ ref('sl_hosts') }} h
LEFT JOIN {{ ref('sl_listings') }} l ON l.host_id = h.host_id
GROUP BY h.host_id, h.host_name, h.is_superhost
ORDER BY nb_listings DESC
