WITH opav1 AS(
      SELECT
          REPLACE(base_xdapp_damaged.dc_routing_code, 'CAJ', 'CJ2') AS responsible_routing_code_1,
          (TO_CHAR(DATE_TRUNC('month', "base_xdapp_damaged"."created"), 'YYYY-MM')) AS month,
          COUNT(base_xdapp_damaged.damaged_id ) AS count_d
      FROM
          "dbt_dw"."lsd_package" AS "lsd_package"
          LEFT JOIN "dbt_dw"."base_xdapp_damaged" AS "base_xdapp_damaged" ON "lsd_package"."n1pk_package_id" = "base_xdapp_damaged"."package_id"
      WHERE ((REPLACE( "base_xdapp_damaged"."dc_routing_code" , 'CAJ', 'CJ2')) <> 'CAJ' OR (REPLACE( "base_xdapp_damaged"."dc_routing_code" , 'CAJ', 'CJ2')) IS NULL)
      GROUP BY
          (DATE_TRUNC('month', "base_xdapp_damaged"."created")),
          1
      ORDER BY
          3 DESC
      )
      SELECT
          "package_process_deadline"."started_at_dc_routing_code" AS routing_code,
          (TO_CHAR(DATE_TRUNC('month', CONVERT_TIMEZONE('America/Sao_Paulo', package_process_deadline.started_at_time) ), 'YYYY-MM')) AS month,
          -- COUNT(DISTINCT "base_package"."n1pk_package_id") AS "count_of_id",
          (CAST(count_d AS DECIMAL) / (COUNT(DISTINCT "base_package"."n1pk_package_id"))) * 1000 AS opav
      FROM
          "dbt_dw"."base_package" AS "base_package"
          LEFT JOIN "prodpostgres"."promiseland_packageprocessdeadline" AS "package_process_deadline" ON "base_package"."n1pk_package_id" = "package_process_deadline"."package_id"
          LEFT JOIN opav1 ON started_at_dc_routing_code = responsible_routing_code_1 AND month = (TO_CHAR(DATE_TRUNC('month', CONVERT_TIMEZONE('America/Sao_Paulo', package_process_deadline.started_at_time) ), 'YYYY-MM'))
      WHERE package_process_deadline.macro_process IN (2, 4)
      AND ("package_process_deadline"."started_at_dc_routing_code" IS NULL OR "package_process_deadline"."started_at_dc_routing_code" <> 'CAJ')
      AND EXTRACT(YEAR FROM package_process_deadline.started_at_time) = EXTRACT(YEAR FROM CURRENT_DATE)
      GROUP BY
          (DATE_TRUNC('month', CONVERT_TIMEZONE('America/Sao_Paulo', package_process_deadline.started_at_time) )),
          1,
          opav1.count_d