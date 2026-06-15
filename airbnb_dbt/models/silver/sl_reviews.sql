SELECT
    CAST(listing_id AS BIGINT)  AS listing_id,
    CAST(date AS DATE)          AS review_date,
    reviewer_name,
    comments,
    sentiment
FROM {{ ref('br_reviews') }}
WHERE listing_id IS NOT NULL
