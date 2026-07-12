USE BCPL_CostLeakage;

-- ══════════════════════════════════════════════════
-- CHECK 1: Row Counts
-- ══════════════════════════════════════════════════
SELECT 'dim_supplier'           AS table_name, COUNT(*) AS row_count FROM dim_supplier
UNION ALL
SELECT 'dim_product',                          COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_warehouse',                        COUNT(*) FROM dim_warehouse
UNION ALL
SELECT 'dim_route',                            COUNT(*) FROM dim_route
UNION ALL
SELECT 'dim_date',                             COUNT(*) FROM dim_date
UNION ALL
SELECT 'fact_purchase_orders',                 COUNT(*) FROM fact_purchase_orders
UNION ALL
SELECT 'fact_inventory_snapshot',              COUNT(*) FROM fact_inventory_snapshot
UNION ALL
SELECT 'fact_shipments',                       COUNT(*) FROM fact_shipments
UNION ALL
SELECT 'fact_order_fulfillment',               COUNT(*) FROM fact_order_fulfillment;

-- ══════════════════════════════════════════════════
-- CHECK 2: FK Integrity — Orphan Records
-- ══════════════════════════════════════════════════
-- fact_po → dim_supplier
SELECT 'fact_po → dim_supplier orphans' AS check_name,
       COUNT(*) AS orphan_count
FROM fact_purchase_orders po
LEFT JOIN dim_supplier s ON po.supplier_id = s.supplier_id
WHERE s.supplier_id IS NULL

UNION ALL
-- fact_po → dim_product
SELECT 'fact_po → dim_product orphans',
       COUNT(*)
FROM fact_purchase_orders po
LEFT JOIN dim_product p ON po.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL
-- fact_inv → dim_warehouse
SELECT 'fact_inv → dim_warehouse orphans',
       COUNT(*)
FROM fact_inventory_snapshot inv
LEFT JOIN dim_warehouse w ON inv.warehouse_id = w.warehouse_id
WHERE w.warehouse_id IS NULL

UNION ALL
-- fact_shp → dim_route
SELECT 'fact_shp → dim_route orphans',
       COUNT(*)
FROM fact_shipments shp
LEFT JOIN dim_route r ON shp.route_id = r.route_id
WHERE r.route_id IS NULL

UNION ALL
-- fact_ful → fact_po
SELECT 'fact_ful → fact_po orphans',
       COUNT(*)
FROM fact_order_fulfillment ful
LEFT JOIN fact_purchase_orders po ON ful.po_id = po.po_id
WHERE po.po_id IS NULL;

-- ══════════════════════════════════════════════════
-- CHECK 3: Business Logic Spot Check
-- ══════════════════════════════════════════════════

-- Negative prices?
SELECT 'Negative actual_unit_price' AS check_name,
       COUNT(*) AS issue_count
FROM fact_purchase_orders
WHERE actual_unit_price < 0

UNION ALL
-- Negative holding cost?
SELECT 'Negative holding_cost',
       COUNT(*)
FROM fact_inventory_snapshot
WHERE holding_cost < 0

UNION ALL
-- Negative freight?
SELECT 'Negative actual_freight_cost',
       COUNT(*)
FROM fact_shipments
WHERE actual_freight_cost < 0

UNION ALL
-- Late penalty negative?
SELECT 'Negative late_penalty',
       COUNT(*)
FROM fact_shipments
WHERE late_penalty < 0

UNION ALL
-- Return/status mismatch?
SELECT 'is_return=1 but not Returned',
       COUNT(*)
FROM fact_order_fulfillment
WHERE is_return = 1 AND order_status != 'Returned';

-- ══════════════════════════════════════════════════
-- CHECK 4: Quick Leakage Preview
-- ══════════════════════════════════════════════════

-- Top 3 suppliers by avg price variance
SELECT TOP 3
    s.supplier_name,
    ROUND(AVG((po.actual_unit_price - po.standard_unit_price)
        / po.standard_unit_price * 100), 2) AS avg_variance_pct
FROM fact_purchase_orders po
JOIN dim_supplier s ON po.supplier_id = s.supplier_id
GROUP BY s.supplier_name
ORDER BY avg_variance_pct DESC;

-- Total logistics leakage by route
SELECT
    r.route_name,
    ROUND(SUM(shp.actual_freight_cost - shp.planned_freight_cost), 2) AS freight_overrun,
    SUM(shp.late_penalty) AS total_penalty
FROM fact_shipments shp
JOIN dim_route r ON shp.route_id = r.route_id
GROUP BY r.route_name
ORDER BY freight_overrun DESC;