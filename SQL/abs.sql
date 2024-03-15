WITH abs AS (
SELECT 
    *,
    CASE 
        WHEN CAST(dc_number AS INTEGER) = 1392 THEN 614
        WHEN CAST(dc_number AS INTEGER) = 1151 THEN 1310
        WHEN CAST(dc_number AS INTEGER) = 112 THEN 549
        ELSE CAST(dc_number AS INTEGER)
    END as new_dc_number
FROM cogs_hc.lex_abs lex
)
SELECT 
routing_code,
TO_CHAR(ref_date::date, 'YYYY-MM') AS month,
ROUND(abs_qtd / total_qtd, 2) AS abs
FROM abs
LEFT JOIN dbt_dw.base_distribution_center AS base_dist_center ON new_dc_number = base_dist_center.id 
WHERE base_dist_center.active = 'true'
GROUP BY month, routing_code, abs_qtd, total_qtd
