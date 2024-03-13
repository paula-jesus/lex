        SELECT 
          TO_CHAR(ref_date::date, 'YYYY-MM') AS month,
          SUM(cnt_two_hrs) AS two_hrs,
          SUM(cnt_interjornada) AS cnt_interjornada,
          routing_code
          FROM cogs_hc.lex_jou_events lex
          LEFT JOIN dbt_dw.base_distribution_center AS base_dist_center ON dc_number = base_dist_center.id 
          WHERE active = 'true'
          group by month, routing_code