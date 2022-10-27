WITH
stg_input AS (SELECT * FROM {{ ref('stg_fruit_user_input') }}),

stg_fact AS (SELECT * FROM {{ ref('stg_fruit_prices_fact') }})

SELECT
    stg_fact."fruit_name",
    stg_input."user_name",
    stg_input."quantity" * stg_fact."cost" AS "total"
FROM
    stg_input LEFT JOIN stg_fact
    ON stg_input."fruit_name" = stg_fact."fruit_name"
