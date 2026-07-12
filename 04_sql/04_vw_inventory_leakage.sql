USE BCPL_CostLeakage;
GO

-- ══════════════════════════════════════════════════
-- VIEW: vw_inventory_holding_leakage
-- Purpose: Dead stock + excess holding cost
--          inventory leakage identify kora
-- ══════════════════════════════════════════════════

CREATE VIEW vw_inventory_holding_leakage AS
SELECT
    inv.snapshot_id,
    inv.snapshot_date,
    inv.opening_stock,
    inv.closing_stock,
    inv.avg_stock_value,
    inv.stock_age_days,
    inv.is_dead_stock,
    inv.holding_cost,

    -- Leakage flag (dead stock only)
    CASE
        WHEN inv.is_dead_stock = 1 THEN inv.holding_cost
        ELSE 0
    END AS dead_stock_holding_cost,

    -- Stock age bucket
    CASE
        WHEN inv.stock_age_days <= 30  THEN '0-30 days'
        WHEN inv.stock_age_days <= 60  THEN '31-60 days'
        WHEN inv.stock_age_days <= 90  THEN '61-90 days'
        WHEN inv.stock_age_days <= 120 THEN '91-120 days'
        ELSE '120+ days'
    END AS stock_age_bucket,

    -- Product info
    p.product_id,
    p.product_name,
    p.category      AS product_category,
    p.standard_cost,

    -- Warehouse info
    w.warehouse_id,
    w.warehouse_name,
    w.location      AS warehouse_location,
    w.type          AS warehouse_type,

    -- Date info
    d.month_name,
    d.quarter,
    d.year

FROM fact_inventory_snapshot inv
JOIN dim_product   p ON inv.product_id   = p.product_id
JOIN dim_warehouse w ON inv.warehouse_id = w.warehouse_id
JOIN dim_date      d ON inv.date_id      = d.date_id;
GO

-- ══════════════════════════════════════════════════
-- TEST QUERIES
-- ══════════════════════════════════════════════════

-- 1. Total leakage by warehouse
SELECT
    warehouse_name,
    warehouse_location,
    COUNT(CASE WHEN is_dead_stock = 1 THEN 1 END)   AS dead_stock_skus,
    ROUND(SUM(holding_cost), 2)                      AS total_holding_cost,
    ROUND(SUM(dead_stock_holding_cost), 2)           AS dead_stock_leakage
FROM vw_inventory_holding_leakage
GROUP BY warehouse_name, warehouse_location
ORDER BY dead_stock_leakage DESC;

-- 2. Total leakage by product category
SELECT
    product_category,
    COUNT(CASE WHEN is_dead_stock = 1 THEN 1 END)   AS dead_stock_count,
    ROUND(SUM(dead_stock_holding_cost), 2)           AS dead_stock_leakage,
    ROUND(AVG(CASE WHEN is_dead_stock = 1
        THEN stock_age_days END), 1)                 AS avg_dead_stock_age
FROM vw_inventory_holding_leakage
GROUP BY product_category
ORDER BY dead_stock_leakage DESC;

-- 3. Stock age distribution
SELECT
    stock_age_bucket,
    COUNT(*)                                         AS snapshot_count,
    ROUND(SUM(holding_cost), 2)                      AS total_holding_cost
FROM vw_inventory_holding_leakage
GROUP BY stock_age_bucket
ORDER BY
    CASE stock_age_bucket
        WHEN '0-30 days'   THEN 1
        WHEN '31-60 days'  THEN 2
        WHEN '61-90 days'  THEN 3
        WHEN '91-120 days' THEN 4
        ELSE 5
    END;

-- 4. Top 10 worst dead stock SKUs
SELECT TOP 10
    product_name,
    product_category,
    warehouse_name,
    stock_age_days,
    ROUND(dead_stock_holding_cost, 2) AS leakage_tk
FROM vw_inventory_holding_leakage
WHERE is_dead_stock = 1
ORDER BY leakage_tk DESC;