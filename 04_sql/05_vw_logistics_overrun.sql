USE BCPL_CostLeakage;
GO

-- ══════════════════════════════════════════════════
-- VIEW: vw_logistics_cost_overrun
-- Purpose: Route-wise planned vs actual freight
--          cost gap — logistics leakage identify
-- ══════════════════════════════════════════════════

CREATE VIEW vw_logistics_cost_overrun AS
SELECT
    shp.shipment_id,
    shp.shipment_date,
    shp.delivery_status,
    shp.planned_freight_cost,
    shp.actual_freight_cost,
    shp.planned_distance_km,
    shp.actual_distance_km,
    shp.late_penalty,

    -- Freight cost overrun
    ROUND(shp.actual_freight_cost - shp.planned_freight_cost, 2)
        AS freight_overrun,

    -- Freight overrun %
    ROUND(
        (shp.actual_freight_cost - shp.planned_freight_cost)
        / shp.planned_freight_cost * 100, 2)
        AS overrun_pct,

    -- Distance overrun
    ROUND(shp.actual_distance_km - shp.planned_distance_km, 2)
        AS distance_overrun_km,

    -- Total logistics leakage per shipment
    ROUND(
        (shp.actual_freight_cost - shp.planned_freight_cost)
        + shp.late_penalty, 2)
        AS total_leakage_per_shipment,

    -- Leakage flag
    CASE
        WHEN ((shp.actual_freight_cost - shp.planned_freight_cost)
            / shp.planned_freight_cost * 100) > 10
        THEN 1 ELSE 0
    END AS is_leakage_flagged,

    -- Late delivery flag
    CASE
        WHEN shp.delivery_status = 'Late'   THEN 1
        WHEN shp.delivery_status = 'Failed' THEN 1
        ELSE 0
    END AS is_late,

    -- Route info
    r.route_id,
    r.route_name,
    r.route_type,
    r.planned_distance_km   AS standard_distance_km,
    r.cost_per_km,

    -- Warehouse info
    w.warehouse_id,
    w.warehouse_name,
    w.location              AS warehouse_location,

    -- Date info
    d.month_name,
    d.quarter,
    d.year

FROM fact_shipments shp
JOIN dim_route     r ON shp.route_id     = r.route_id
JOIN dim_warehouse w ON shp.warehouse_id = w.warehouse_id
JOIN dim_date      d ON shp.date_id      = d.date_id;
GO

-- ══════════════════════════════════════════════════
-- TEST QUERIES
-- ══════════════════════════════════════════════════

-- 1. Total leakage by route
SELECT
    route_name,
    route_type,
    COUNT(shipment_id)                          AS total_shipments,
    ROUND(AVG(overrun_pct), 2)                  AS avg_overrun_pct,
    ROUND(SUM(freight_overrun), 2)              AS total_freight_overrun,
    ROUND(SUM(late_penalty), 2)                 AS total_late_penalty,
    ROUND(SUM(total_leakage_per_shipment), 2)   AS total_leakage_tk
FROM vw_logistics_cost_overrun
GROUP BY route_name, route_type
ORDER BY total_leakage_tk DESC;

-- 2. Late delivery rate by route
SELECT
    route_name,
    COUNT(shipment_id)                              AS total_shipments,
    SUM(is_late)                                    AS late_shipments,
    ROUND(SUM(is_late) * 100.0 / COUNT(*), 1)      AS late_pct,
    ROUND(SUM(late_penalty), 2)                     AS total_penalty_tk
FROM vw_logistics_cost_overrun
GROUP BY route_name
ORDER BY late_pct DESC;

-- 3. Monthly leakage trend
SELECT
    month_name,
    quarter,
    ROUND(SUM(total_leakage_per_shipment), 2)   AS monthly_leakage_tk,
    COUNT(shipment_id)                           AS shipment_count
FROM vw_logistics_cost_overrun
GROUP BY month_name, quarter
ORDER BY quarter, MIN(shipment_date);

-- 4. Flagged vs non-flagged summary
SELECT
    is_leakage_flagged,
    COUNT(*)                                        AS shipment_count,
    ROUND(SUM(total_leakage_per_shipment), 2)       AS total_leakage_tk
FROM vw_logistics_cost_overrun
GROUP BY is_leakage_flagged;