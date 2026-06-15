SELECT
    CAST(id AS BIGINT)              AS host_id,
    name                           AS host_name,
    (is_superhost = 't')           AS is_superhost,
    CAST(created_at AS TIMESTAMP)  AS created_at
FROM {{ ref('br_hosts') }}
WHERE id IS NOT NULL
