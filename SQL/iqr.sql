WITH iqr AS (
    SELECT
        COALESCE(itinerary.distribution_center_route_processing, base_offer.distribution_center) AS dc,
        base_offer.dc_routing_code AS routing_code,
        TO_CHAR(DATE_TRUNC('month', itinerary.created), 'YYYY-MM') AS month,
        transport_type,
        AVG(CASE WHEN itinerary.transport_type = 'Carro' AND itinerary.waypoints_without_return > 0 THEN (itinerary.distance_without_return::decimal / itinerary.waypoints_without_return) / 1000 END) AS carro_densidade,
        AVG(CASE WHEN itinerary.transport_type = 'Moto' AND itinerary.waypoints_without_return > 0 THEN (itinerary.distance_without_return::decimal / itinerary.waypoints_without_return) / 1000 END) AS moto_densidade,
        AVG(CASE WHEN itinerary.transport_type = 'Carro' THEN itinerary.packages END) AS carro_pacotes,
        AVG(CASE WHEN itinerary.transport_type = 'Moto' THEN itinerary.packages END) AS moto_pacotes
    FROM
        dbt_dw.base_itinerary AS itinerary
    LEFT JOIN
        dbt_dw.base_offer AS base_offer ON itinerary.n1pk_itinerary_id = base_offer.itinerary_id AND itinerary.driver_id = base_offer.driver_id
    WHERE
        itinerary.created >= TIMESTAMP '2024-07-01' 
        AND itinerary.fleet_type = 'MEI'
        AND itinerary.product = 'Pro'
        AND itinerary.status IN ('awaiting_completion', 'cancelledWithCharge', 'finished', 'requires_verification')
        AND itinerary.transport_type IN ('Carro', 'Moto')
        AND (NOT base_offer.is_pickup OR base_offer.is_pickup IS NULL)
    GROUP BY
        1, 2, 3, 4
),

metas_iqr_agencia_modal AS (
    SELECT
        distribution_center,
        meta_pacote,
        meta_densidade,
        transport_type,
        TO_CHAR(DATE_TRUNC('month', month), 'YYYY-MM') AS month
    FROM
        business_analytics.metas_iqr_agencia_modal
)

SELECT
    iqr.routing_code AS routing_code,
    iqr.month,
    LEAST(1, MAX(CASE WHEN iqr.transport_type = 'Carro' THEN
            CASE WHEN metas.meta_pacote <> 0 THEN
                ((1 - ((metas.meta_pacote - iqr.carro_pacotes) / metas.meta_pacote)) * 0.65)
                + ((1 - ((iqr.carro_densidade - metas.meta_densidade) / metas.meta_densidade)) * 0.35)
            ELSE NULL END
        ELSE NULL END)) AS iqr_carro,
    LEAST(1, MAX(CASE WHEN iqr.transport_type = 'Moto' THEN
            CASE WHEN metas.meta_pacote <> 0 THEN
                ((1 - ((metas.meta_pacote - iqr.moto_pacotes) / metas.meta_pacote)) * 0.65)
                + ((1 - ((iqr.moto_densidade - metas.meta_densidade) / metas.meta_densidade)) * 0.35)
            ELSE NULL END
        ELSE NULL END)) AS iqr_moto
FROM
    metas_iqr_agencia_modal metas
LEFT JOIN
    iqr ON metas.transport_type = iqr.transport_type
        AND metas.month = iqr.month
        AND metas.distribution_center = iqr.dc
GROUP BY
    iqr.routing_code,
    iqr.month
ORDER BY
    iqr.routing_code,
    iqr.month;
