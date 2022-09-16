WITH
fruit_join AS (
    SELECT * FROM {{ ref('fruit_join') }}
)

SELECT
    "user_name",
    SUM("total") AS "total_final"

FROM fruit_join
WHERE "user_name" IS NOT NULL
GROUP BY "user_name"
ORDER BY SUM("total") DESC
