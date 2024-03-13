SELECT
    TO_CHAR(DATE_TRUNC('month', pih.Reference_date), 'YYYY-MM') AS "month",
    routing_code,
    -- COALESCE(SUM(pih.inventoried_packages), 0) AS "sum_inventoried_packages",
    -- COALESCE(SUM(pih.non_inventoried_packages), 0) AS "sum_non_inventoried_packages",
    ROUND(COALESCE(SUM(pih.inventoried_packages), 0) * 100.0 / NULLIF((SUM(pih.inventoried_packages) + SUM(pih.non_inventoried_packages)), 0), 2) AS percent_inventoried
FROM
    dbt_dw.package_inventory_history AS pih
WHERE
    pih.custody_owner_type NOT IN ('Entregador MEI', 'Entregador leve', 'Base leve', 'Mid-mile', 'Posto Avançado') 
    AND EXTRACT(YEAR FROM pih.Reference_date) = EXTRACT(YEAR FROM CURRENT_DATE)
    AND (TRIM(TO_CHAR(pih.Reference_date, 'Day')) <> 'Sunday' OR TRIM(TO_CHAR(pih.Reference_date, 'Day')) IS NULL)
GROUP BY
    TO_CHAR(DATE_TRUNC('month', pih.Reference_date), 'YYYY-MM'),
    pih.distribution_center_name,
    routing_code
ORDER BY
    month DESC
