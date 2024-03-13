with daily_people AS (
        SELECT
          DATE("created_timezone_loggi") AS created_date,
          COUNT(DISTINCT CASE WHEN base_employees.job_name IS NULL OR  base_employees.job_name   LIKE (CAST('%' AS VARCHAR) || CAST(REPLACE(REPLACE('Auxiliar', '%', '\\%'), '_', '\\_') AS VARCHAR) || CAST('%' AS VARCHAR)) THEN base_process.op_id  ELSE NULL END) AS pessoas,
          COUNT(DISTINCT "package_id") AS pacotes,
          base_dist_center.routing_code AS routing_code,
          base_dist_center.type_dc,
          (TO_CHAR(DATE_TRUNC('month', "created_timezone_loggi"), 'YYYY-MM')) AS month
        FROM
          dbt_dw.base_process base_process
        LEFT JOIN dbt_dw.base_distribution_center AS base_dist_center ON base_process.dc_name = base_dist_center.name
        LEFT JOIN people_data.people_individual  AS base_employees ON base_employees.email = base_process.op_email
        WHERE EXTRACT(YEAR FROM created_date) = EXTRACT(YEAR FROM CURRENT_DATE)
        AND base_process.type_dc IN ('Crossdocking','Agência')
        AND base_process.process IN ('PRE', 'Separação')
        GROUP BY
          DATE("created_timezone_loggi"),
          4,
          5,
          6
      )
      SELECT
        routing_code,
        month,
        type_dc,
        SUM(pacotes) / SUM(pessoas) AS produtividade_media
      FROM daily_people
      GROUP BY 1, 2, 3