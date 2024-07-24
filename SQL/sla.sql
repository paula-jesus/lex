WITH ags AS (
SELECT
    base_package.planned_routing_code  AS "routing_code",
    (TO_CHAR(DATE_TRUNC('month', package_deadline.promiseddate ), 'YYYY-MM')) AS "month",
    ( COUNT(CASE WHEN (( package_deadline.package_sla_achievement  ) = 'Dentro do prazo') THEN 1 ELSE NULL END) )*1.0/NULLIF(( COUNT(CASE WHEN  package_deadline.is_deliverable   THEN 1 ELSE NULL END) ),0)  AS "sla"
FROM dbt_dw.base_package  AS base_package
LEFT JOIN dbt_dw.package_deadline  AS package_deadline ON base_package.n1pk_package_id = package_deadline.n1pk_package_id
WHERE EXTRACT(YEAR FROM package_deadline.promiseddate) = EXTRACT(YEAR FROM CURRENT_DATE)
AND base_package.planned_routing_code NOT LIKE '%XD%' AND base_package.planned_routing_code NOT LIKE '%CJ2%'
GROUP BY
    (DATE_TRUNC('month', package_deadline.promiseddate )),
    1
),

xds AS (
SELECT
    TRIM('"' FROM UPPER(base_package.confirmation_hub_routing_code::VARCHAR))  AS "routing_code",
    (TO_CHAR(DATE_TRUNC('month', package_deadline.promiseddate ), 'YYYY-MM')) AS "month",
    ( COUNT(CASE WHEN (( package_deadline.package_sla_achievement  ) = 'Dentro do prazo') THEN 1 ELSE NULL END) )*1.0/NULLIF(( COUNT(CASE WHEN  package_deadline.is_deliverable   THEN 1 ELSE NULL END) ),0)  AS "sla"
FROM
    "dbt_dw"."base_package" AS "base_package"
    LEFT JOIN "dbt_dw"."package_deadline" AS "package_deadline" ON "base_package"."n1pk_package_id" = "package_deadline"."n1pk_package_id"
WHERE ((TRIM('"' FROM UPPER(base_package.confirmation_hub_routing_code::VARCHAR)) ) LIKE '%XD%' OR (TRIM('"' FROM UPPER(base_package.confirmation_hub_routing_code::VARCHAR)) ) LIKE '%CJ2%') 
AND EXTRACT(YEAR FROM package_deadline.promiseddate) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY
    1,
    (DATE_TRUNC('month', package_deadline.promiseddate ))
)

SELECT * FROM ags
UNION ALL
SELECT * FROM xds
ORDER BY "routing_code", "month";