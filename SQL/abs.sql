        SELECT 
          TO_CHAR(ref_date::date, 'YYYY-MM') AS month,
          ROUND(abs_qtd / total_qtd, 2) AS abs,
          routing_code
          FROM cogs_hc.lex_abs abs
          LEFT JOIN dbt_dw.base_distribution_center AS base_dist_center ON dc_number = base_dist_center.id 
          WHERE active = 'true'
          group by month, routing_code, abs_qtd, total_qtd