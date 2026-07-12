USE BCPL_CostLeakage;
GO

-- ══════════════════════════════════════════════════
-- VIEW: vw_leakage_by_supplier_route
-- Purpose: Pareto analysis — kon 20% supplier/route
--          80% leakage create korche
-- ══════════════════════════════════════════════════

CREATE VIEW vw_leakage_by_supplier_route AS

-- Supplier-wise procurement leakage
SELECT
    'Supplier'                          AS dimension_type,
    s.supplier_id                       AS entity_id,
    s.supplier_name                     AS entity_name,
    s.supplier_type                     AS entity_subtype,
    'Procurement'                       AS leakage_category,
    ROUND(SUM(
        (po.actual_unit_price - po.standard_unit_price)
        * po.quantity_ordered
    ), 2)                               AS leakage_amount,
    COUNT(po.po_id)                     AS transaction_count
FROM fact_purchase_orders po
JOIN dim_supplier s ON po.supplier_id = s.supplier_id
WHERE po.po_status = 'Completed'
  AND po.actual_unit_price > po.standard_unit_price
GROUP BY s.supplier_id, s.supplier_name, s.supplier_type

UNION ALL

-- Route-wise logistics leakage
SELECT
    'Route'                             AS dimension_type,
    r.route_id                          AS entity_id,
    r.route_name                        AS entity_name,
    r.route_type                        AS entity_subtype,
    'Logistics'                         AS leakage_category,
    ROUND(SUM(
        (shp.actual_freight_cost - shp.planned_freight_cost)
        + shp.late_penalty
    ), 2)                               AS leakage_amount,
    COUNT(shp.shipment_id)              AS transaction_count
FROM fact_shipments shp
JOIN dim_route r ON shp.route_id = r.route_id
WHERE shp.actual_freight_cost > shp.planned_freight_cost
   OR shp.late_penalty > 0
GROUP BY r.route_id, r.route_name, r.route_type

UNION ALL

-- Warehouse-wise inventory leakage
SELECT
    'Warehouse'                         AS dimension_type,
    w.warehouse_id                      AS entity_id,
    w.warehouse_name                    AS entity_name,
    w.type                              AS entity_subtype,
    'Inventory'                         AS leakage_category,
    ROUND(SUM(inv.holding_cost), 2)     AS leakage_amount,
    COUNT(inv.snapshot_id)              AS transaction_count
FROM fact_inventory_snapshot inv
JOIN dim_warehouse w ON inv.warehouse_id = w.warehouse_id
WHERE inv.is_dead_stock = 1
GROUP BY w.warehouse_id, w.warehouse_name, w.type

UNION ALL

-- Warehouse-wise fulfillment leakage
SELECT
    'Warehouse'                         AS dimension_type,
    w.warehouse_id                      AS entity_id,
    w.warehouse_name                    AS entity_name,
    w.type                              AS entity_subtype,
    'Fulfillment'                       AS leakage_category,
    ROUND(SUM(
        ful.return_cost + ful.partial_extra_cost
    ), 2)                               AS leakage_amount,
    COUNT(ful.fulfillment_id)           AS transaction_count
FROM fact_order_fulfillment ful
JOIN dim_warehouse w ON ful.warehouse_id = w.warehouse_id
WHERE ful.order_status IN ('Returned', 'Partial')
GROUP BY w.warehouse_id, w.warehouse_name, w.type;
GO

-- ══════════════════════════════════════════════════
-- TEST QUERIES
-- ══════════════════════════════════════════════════

-- 1. Top contributors — all dimensions ranked
SELECT
    dimension_type,
    entity_name,
    entity_subtype,
    leakage_category,
    leakage_amount,
    transaction_count,
    ROUND(leakage_amount * 100.0 /
        SUM(leakage_amount) OVER(PARTITION BY leakage_category), 2)
        AS pct_of_category_leakage
FROM vw_leakage_by_supplier_route
ORDER BY leakage_amount DESC;

-- 2. Pareto — Supplier leakage
SELECT
    entity_name,
    entity_subtype,
    leakage_amount,
    ROUND(SUM(leakage_amount) OVER(
        ORDER BY leakage_amount DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) * 100.0 / SUM(leakage_amount) OVER(), 2) AS cumulative_pct
FROM vw_leakage_by_supplier_route
WHERE dimension_type = 'Supplier'
ORDER BY leakage_amount DESC;

-- 3. Pareto — Route leakage
SELECT
    entity_name,
    entity_subtype,
    leakage_amount,
    ROUND(SUM(leakage_amount) OVER(
        ORDER BY leakage_amount DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) * 100.0 / SUM(leakage_amount) OVER(), 2) AS cumulative_pct
FROM vw_leakage_by_supplier_route
WHERE dimension_type = 'Route'
ORDER BY leakage_amount DESC;

-- 4. 80/20 summary — top 3 suppliers
SELECT TOP 3
    entity_name,
    entity_subtype,
    leakage_amount,
    ROUND(leakage_amount * 100.0 /
        SUM(leakage_amount) OVER(), 2) AS pct_of_total_supplier_leakage
FROM vw_leakage_by_supplier_route
WHERE dimension_type = 'Supplier'
ORDER BY leakage_amount DESC;