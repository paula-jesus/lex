WITH jou AS (
SELECT 
    *,
    CASE 
        WHEN CAST(dc_number AS INTEGER) = 1392 THEN 614
        WHEN CAST(dc_number AS INTEGER) = 1151 THEN 1310
        WHEN CAST(dc_number AS INTEGER) = 112 THEN 549
        ELSE CAST(dc_number AS INTEGER)
    END as new_dc_number
FROM cogs_hc.lex_jou_events lex
)
SELECT 
routing_code,
TO_CHAR(ref_date::date, 'YYYY-MM') AS month,
SUM(cnt_two_hrs) AS two_hrs,
SUM(cnt_interjornada) AS cnt_interjornada
FROM jou
LEFT JOIN dbt_dw.base_distribution_center AS base_dist_center ON new_dc_number = base_dist_center.id 
WHERE base_dist_center.active = 'true'
GROUP BY month, routing_code
