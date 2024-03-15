WITH pcts AS (
SELECT
    package_process_deadline.started_at_dc_routing_code  AS routing_code,
    (TO_CHAR(DATE_TRUNC('month', package_deadline.first_validation ), 'YYYY-MM')) AS month,
    COUNT(DISTINCT base_package.n1pk_package_id ) AS count_packages
FROM dbt_dw.base_package  AS base_package
LEFT JOIN dbt_dw.package_deadline  AS package_deadline ON base_package.n1pk_package_id = package_deadline.n1pk_package_id
LEFT JOIN prodpostgres.promiseland_packageprocessdeadline  AS package_process_deadline ON package_process_deadline.package_id = base_package.n1pk_package_id
WHERE EXTRACT(YEAR FROM package_deadline.first_validation ) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY
    (DATE_TRUNC('month', package_deadline.first_validation )),
    1
)
, lsd AS(
SELECT
    COALESCE(lsd_loss_custody.loss_dc_routing_code, last_enriched_sorting_record.routing_code)  AS routing_code,
    (TO_CHAR(DATE_TRUNC('month', analytics_package.first_lsd_internal_status_updated ), 'YYYY-MM')) AS month,
    COALESCE(SUM(CASE WHEN (( lsd_package.current_internal_status_label  ) = 'Mercadoria avariada') THEN lsd_package.goods_value  ELSE NULL END), 0) + COALESCE(SUM(CASE WHEN (( lsd_package.current_internal_status_label  ) = 'Pacote extraviado') THEN lsd_package.goods_value  ELSE NULL END), 0) + COALESCE(SUM(CASE WHEN (( lsd_package.current_internal_status_label  ) = 'Roubo / Furto') THEN lsd_package.goods_value  ELSE NULL END), 0) AS sum_loss
FROM dbt_dw.lsd_package  AS lsd_package
LEFT JOIN dbt_dw.analytics_package  AS analytics_package ON lsd_package.n1pk_package_id = analytics_package.package_id
LEFT JOIN dbt_dw.last_enriched_sorting_record  AS last_enriched_sorting_record ON last_enriched_sorting_record.package_id = lsd_package.n1pk_package_id
LEFT JOIN dbt_dw.loss_custody  AS lsd_loss_custody ON lsd_loss_custody.n1pk_package_id = lsd_package.n1pk_package_id
WHERE EXTRACT(YEAR FROM analytics_package.first_lsd_internal_status_updated ) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY
    (DATE_TRUNC('month', analytics_package.first_lsd_internal_status_updated)),
    1
)
SELECT 
pcts.routing_code,
pcts.month,
-- count_packages,
-- sum_loss,
ROUND((sum_loss / count_packages), 2) AS loss_rate
FROM lsd 
LEFT JOIN pcts ON lsd.routing_code = pcts.routing_code AND lsd.month = pcts.month
