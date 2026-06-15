SELECT
    CAST(id AS BIGINT)                              AS listing_id,
    CAST(host_id AS BIGINT)                         AS host_id,
    name                                            AS listing_name,
    room_type,
    CAST(minimum_nights AS INTEGER)                 AS minimum_nights,
    CAST(REPLACE(REPLACE(price, '$', ''), ',', '') AS DOUBLE) AS price
FROM {{ ref('br_listings') }}
WHERE id IS NOT NULL
