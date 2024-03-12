WITH opav1 AS(
      SELECT
          REPLACE(base_xdapp_damaged.dc_routing_code, 'CAJ', 'CJ2') AS responsible_routing_code_1,
          (TO_CHAR(DATE_TRUNC('month', "base_xdapp_damaged"."created"), 'YYYY-MM')) AS month,
          COUNT(base_xdapp_damaged.damaged_id ) AS count_d
      FROM
          "dbt_dw"."lsd_package" AS "lsd_package"
          LEFT JOIN "dbt_dw"."base_xdapp_damaged" AS "base_xdapp_damaged" ON "lsd_package"."n1pk_package_id" = "base_xdapp_damaged"."package_id"
      WHERE ((REPLACE( "base_xdapp_damaged"."dc_routing_code" , 'CAJ', 'CJ2')) <> 'CAJ' OR (REPLACE( "base_xdapp_damaged"."dc_routing_code" , 'CAJ', 'CJ2')) IS NULL)
      AND month >= 2023-08
      GROUP BY
          (DATE_TRUNC('month', "base_xdapp_damaged"."created")),
          1
      )
      ,
      opav AS(
      SELECT
          "package_process_deadline"."started_at_dc_routing_code" AS started_at_dc_routing_code,
          (TO_CHAR(DATE_TRUNC('month', CONVERT_TIMEZONE('America/Sao_Paulo', package_process_deadline.started_at_time) ), 'YYYY-MM')) AS month,
          count_d,
          COUNT(DISTINCT "base_package"."n1pk_package_id") AS "count_of_id",
          (CAST(count_d AS DECIMAL) / count_of_id) * 1000 AS opav
      FROM
          "dbt_dw"."base_package" AS "base_package"
          LEFT JOIN "prodpostgres"."promiseland_packageprocessdeadline" AS "package_process_deadline" ON "base_package"."n1pk_package_id" = "package_process_deadline"."package_id"
          LEFT JOIN opav1 ON started_at_dc_routing_code = responsible_routing_code_1 AND month = (TO_CHAR(DATE_TRUNC('month', CONVERT_TIMEZONE('America/Sao_Paulo', package_process_deadline.started_at_time) ), 'YYYY-MM'))
      WHERE (CASE
      WHEN package_process_deadline.macro_process = 0  THEN 'Inválido'
      WHEN package_process_deadline.macro_process = 1  THEN 'Coleta'
      WHEN package_process_deadline.macro_process = 2  THEN 'Cross Docking'
      WHEN package_process_deadline.macro_process = 3  THEN 'Transferência'
      WHEN package_process_deadline.macro_process = 4  THEN 'Last Mile Base'
      WHEN package_process_deadline.macro_process = 5  THEN 'Entrega'
      WHEN package_process_deadline.macro_process = 6  THEN 'Redespacho'

      END) IN ('Cross Docking', 'Last Mile Base') AND ("package_process_deadline"."started_at_dc_routing_code" IS NULL OR "package_process_deadline"."started_at_dc_routing_code" <> 'CAJ')
      AND month >= 2023-08
      GROUP BY
          (DATE_TRUNC('month', CONVERT_TIMEZONE('America/Sao_Paulo', package_process_deadline.started_at_time) )),
          1,
          3
      )
      , lossrate AS(
      SELECT
          COALESCE(lsd_loss_custody.loss_dc_routing_code, last_enriched_sorting_record.routing_code)  AS loss_responsible_dc,
              (TO_CHAR(DATE_TRUNC('month', CASE
                    WHEN lsd_package.confirmation IS NOT NULL THEN lsd_package.confirmation
                    WHEN lsd_package.confirmation IS NULL AND (lsd_package.current_internal_status_label IN ('Pacote extraviado', 'Roubo / Furto', 'Mercadoria avariada')) THEN lsd_package.created
                END), 'YYYY-MM')) AS month,
                  (COALESCE(SUM(CASE WHEN (( lsd_package.current_internal_status_label  ) = 'Mercadoria avariada') THEN lsd_package.goods_value  ELSE NULL END), 0) + COALESCE(SUM(CASE WHEN (( lsd_package.current_internal_status_label  ) = 'Pacote extraviado') THEN lsd_package.goods_value  ELSE NULL END), 0) + COALESCE(SUM(CASE WHEN (( lsd_package.current_internal_status_label  ) = 'Roubo / Furto') THEN lsd_package.goods_value  ELSE NULL END), 0)) / nullif(COALESCE(SUM(lsd_package.goods_value ), 0), 0) AS loss_rate
      FROM dbt_dw.lsd_package  AS lsd_package
      LEFT JOIN dbt_dw.last_enriched_sorting_record  AS last_enriched_sorting_record ON last_enriched_sorting_record.package_id = lsd_package.n1pk_package_id

      LEFT JOIN dbt_dw.loss_custody  AS lsd_loss_custody ON lsd_loss_custody.n1pk_package_id = lsd_package.n1pk_package_id
      WHERE ((( CASE
                    WHEN lsd_package.confirmation IS NOT NULL THEN lsd_package.confirmation
                    WHEN lsd_package.confirmation IS NULL AND (lsd_package.current_internal_status_label IN ('Pacote extraviado', 'Roubo / Furto', 'Mercadoria avariada')) THEN lsd_package.created
                END ) >= ((DATEADD(month,-5, DATE_TRUNC('month', DATE_TRUNC('day',GETDATE())) ))) AND ( CASE
                    WHEN lsd_package.confirmation IS NOT NULL THEN lsd_package.confirmation
                    WHEN lsd_package.confirmation IS NULL AND (lsd_package.current_internal_status_label IN ('Pacote extraviado', 'Roubo / Furto', 'Mercadoria avariada')) THEN lsd_package.created
                END ) < ((DATEADD(month,6, DATEADD(month,-5, DATE_TRUNC('month', DATE_TRUNC('day',GETDATE())) ) ))))) AND (COALESCE(lsd_loss_custody.loss_responsible,last_enriched_sorting_record.custody_owner_type) ) IN ('Cajamar', 'XD Regional', 'Agência Loggi')
      AND created >= 2023-08
      GROUP BY
          (DATE_TRUNC('month', CASE
                    WHEN lsd_package.confirmation IS NOT NULL THEN lsd_package.confirmation
                    WHEN lsd_package.confirmation IS NULL AND (lsd_package.current_internal_status_label IN ('Pacote extraviado', 'Roubo / Furto', 'Mercadoria avariada')) THEN lsd_package.created
                END)),
          1
      ORDER BY
          2 DESC
      )
      , daily_people AS (
        SELECT
          DATE("created_timezone_loggi") AS created_date,
          COUNT(DISTINCT CASE WHEN base_employees.job_name IS NULL OR  base_employees.job_name   LIKE (CAST('%' AS VARCHAR) || CAST(REPLACE(REPLACE('Auxiliar', '%', '\\%'), '_', '\\_') AS VARCHAR) || CAST('%' AS VARCHAR)) THEN base_process.op_id  ELSE NULL END) AS pessoas,
          COUNT(DISTINCT "package_id") AS pacotes,
          base_dist_center.routing_code AS routing_code,
          (TO_CHAR(DATE_TRUNC('month', "created_timezone_loggi"), 'YYYY-MM')) AS month,
          base_process.type_dc,
          base_dist_center.id
        FROM
          dbt_dw.base_process base_process
        LEFT JOIN dbt_dw.base_distribution_center AS base_dist_center ON base_process.dc_name = base_dist_center.name
        LEFT JOIN people_data.people_individual  AS base_employees ON base_employees.email = base_process.op_email
        WHERE created_date >= 2023-08
        AND base_process.type_dc IN ('Crossdocking','Agência')
        AND base_process.process IN ('PRE', 'Separação')
        GROUP BY
          DATE("created_timezone_loggi"),
          4,
          5,
          base_process.type_dc,
          base_dist_center.id
      )
      , produtividade AS(
      SELECT
        routing_code,
        month,
        type_dc,
        id,
        SUM(pacotes) / SUM(pessoas) AS produtividade_media
      FROM daily_people
      GROUP BY 1, 2, 3, 4
      )
      , two_hrs AS(
        SELECT 
          TO_CHAR(ref_date::date, 'YYYY-MM') AS month,
          SUM(cnt_two_hrs) AS two_hrs,
          SUM(cnt_interjornada) AS cnt_interjornada,
          dc_number
          from cogs_hc.lex_jou_events
          group by month,dc_number
          )
        , abs AS(
          select 
            TO_CHAR(ref_date::date, 'YYYY-MM') AS month,
            dc_number,
            ROUND(abs_qtd / total_qtd, 2) AS abs
            from cogs_hc.lex_abs
        )
        , sla AS (
        SELECT
            base_package.planned_routing_code  AS "routing_code",
            (TO_CHAR(DATE_TRUNC('month', package_deadline.promiseddate ), 'YYYY-MM')) AS "month",
            ( COUNT(CASE WHEN (( package_deadline.package_sla_achievement  ) = 'Dentro do prazo') THEN 1 ELSE NULL END) )*1.0/NULLIF(( COUNT(CASE WHEN  package_deadline.is_deliverable   THEN 1 ELSE NULL END) ),0)  AS "sla_percentage"
        FROM dbt_dw.base_package  AS base_package
        LEFT JOIN dbt_dw.package_deadline  AS package_deadline ON base_package.n1pk_package_id = package_deadline.n1pk_package_id
        WHERE ((( package_deadline.promiseddate  ) >= ((DATEADD(month,-5, DATE_TRUNC('month', DATE_TRUNC('day',GETDATE())) ))) AND ( package_deadline.promiseddate  ) < ((DATEADD(month,5, DATEADD(month,-5, DATE_TRUNC('month', DATE_TRUNC('day',GETDATE())) ) )))))
        GROUP BY
            (DATE_TRUNC('month', package_deadline.promiseddate )),
            1
        )
      SELECT
          sla.routing_code,
          sla.month,
          produtividade_media,
          ROUND(opav, 2) AS opav,
          loss_rate,
          produtividade.type_dc,
          abs, 
          two_hrs,
          cnt_interjornada,
          sla.sla_percentage
      FROM
          sla 
          LEFT JOIN produtividade ON produtividade.routing_code = sla.routing_code AND produtividade.month = sla.month
          LEFT JOIN lossrate ON lossrate.month = produtividade.month AND loss_responsible_dc = produtividade.routing_code
          LEFT JOIN opav ON opav.started_at_dc_routing_code = loss_responsible_dc and opav.month = produtividade.month
          LEFT JOIN two_hrs ON two_hrs.dc_number = produtividade.id AND two_hrs.month = produtividade.month
          LEFT JOIN abs ON abs.dc_number = produtividade.id AND abs.month = produtividade.month
      WHERE sla.month >= 2023-12
      GROUP BY
          sla.month,
          1,
          produtividade_media,
          opav,
          loss_rate,
          produtividade.type_dc,
          abs, 
          two_hrs,
          cnt_interjornada,
          sla.sla_percentage
      ORDER BY
          2 DESC
