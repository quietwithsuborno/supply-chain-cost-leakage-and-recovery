USE BCPL_CostLeakage;
GO

-- ══════════════════════════════════════════════════
-- VIEW: vw_delivery_penalty_leakage
-- Purpose: Late/Failed delivery penalty cost
--          breakdown — route ar warehouse wise
-- ══════════════════════════════════════════════════

CREATE VIEW vw_delivery_penalty_leakage AS
SELECT
    shp.shipment_id,
    shp.shipment_date,
    shp.delivery_status,
    shp.late_penalty,

    -- Penalty tier
    CASE
        WHEN shp.late_penalty = 0    THEN 'No Penalty'
        WHEN shp.late_penalty = 500  THEN 'Late (৳500)'
        WHEN shp.late_penalty = 1000 THEN 'Failed (৳1000)'
        ELSE 'Other'
    END AS penalty_tier,

    -- Route info
    r.route_id,
    r.route_name,
    r.route_type,
    r.origin_warehouse,

    -- Warehouse info
    w.warehouse_id,
    w.warehouse_name,
    w.location      AS warehouse_location,

    -- Date info
    d.month_name,
    d.quarter,
    d.year

FROM fact_shipments shp
JOIN dim_route     r ON shp.route_id     = r.route_id
JOIN dim_warehouse w ON shp.warehouse_id = w.warehouse_id
JOIN dim_date      d ON shp.date_id      = d.date_id
WHERE shp.delivery_status IN ('Late', 'Failed');
GO

-- ══════════════════════════════════════════════════
-- TEST QUERIES
-- ══════════════════════════════════════════════════

-- 1. Penalty summary by route
SELECT
    route_name,
    route_type,
    COUNT(shipment_id)              AS late_shipments,
    ROUND(SUM(late_penalty), 2)     AS total_penalty_tk,
    ROUND(AVG(late_penalty), 2)     AS avg_penalty_per_shipment
FROM vw_delivery_penalty_leakage
GROUP BY route_name, route_type
ORDER BY total_penalty_tk DESC;

-- 2. Penalty by warehouse
SELECT
    warehouse_name,
    warehouse_location,
    COUNT(shipment_id)              AS late_shipments,
    ROUND(SUM(late_penalty), 2)     AS total_penalty_tk
FROM vw_delivery_penalty_leakage
GROUP BY warehouse_name, warehouse_location
ORDER BY total_penalty_tk DESC;

-- 3. Monthly penalty trend
SELECT
    month_name,
    quarter,
    COUNT(shipment_id)              AS late_shipments,
    ROUND(SUM(late_penalty), 2)     AS monthly_penalty_tk
FROM vw_delivery_penalty_leakage
GROUP BY month_name, quarter
ORDER BY quarter, MIN(shipment_date);

-- 4. Penalty tier breakdown
SELECT
    penalty_tier,
    COUNT(shipment_id)              AS shipment_count,
    ROUND(SUM(late_penalty), 2)     AS total_penalty_tk
FROM vw_delivery_penalty_leakage
GROUP BY penalty_tier
ORDER BY total_penalty_tk DESC;