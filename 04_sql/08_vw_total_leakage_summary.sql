USE BCPL_CostLeakage;
GO

-- ══════════════════════════════════════════════════
-- VIEW: vw_total_leakage_summary
-- Purpose: Shob 4 category leakage ekshathe —
--          executive-level summary view
-- ══════════════════════════════════════════════════

CREATE VIEW vw_total_leakage_summary AS

-- Procurement Leakage
SELECT
    d.year,
    d.quarter,
    d.month_name,
    CAST(d.month AS INT)            AS month_num,
    'Procurement'                   AS leakage_category,
    ROUND(SUM(
        (po.actual_unit_price - po.standard_unit_price)
        * po.quantity_ordered
    ), 2)                           AS leakage_amount
FROM fact_purchase_orders po
JOIN dim_date d ON po.date_id = d.date_id
WHERE po.po_status = 'Completed'
  AND po.actual_unit_price > po.standard_unit_price
GROUP BY d.year, d.quarter, d.month_name, d.month

UNION ALL

-- Inventory Leakage (dead stock only)
SELECT
    d.year,
    d.quarter,
    d.month_name,
    CAST(d.month AS INT),
    'Inventory',
    ROUND(SUM(inv.holding_cost), 2)
FROM fact_inventory_snapshot inv
JOIN dim_date d ON inv.date_id = d.date_id
WHERE inv.is_dead_stock = 1
GROUP BY d.year, d.quarter, d.month_name, d.month

UNION ALL

-- Logistics Leakage (freight overrun + penalty)
SELECT
    d.year,
    d.quarter,
    d.month_name,
    CAST(d.month AS INT),
    'Logistics',
    ROUND(SUM(
        (shp.actual_freight_cost - shp.planned_freight_cost)
        + shp.late_penalty
    ), 2)
FROM fact_shipments shp
JOIN dim_date d ON shp.date_id = d.date_id
WHERE shp.actual_freight_cost > shp.planned_freight_cost
   OR shp.late_penalty > 0
GROUP BY d.year, d.quarter, d.month_name, d.month

UNION ALL

-- Fulfillment Leakage (return + partial)
SELECT
    d.year,
    d.quarter,
    d.month_name,
    CAST(d.month AS INT),
    'Fulfillment',
    ROUND(SUM(ful.return_cost + ful.partial_extra_cost), 2)
FROM fact_order_fulfillment ful
JOIN dim_date d ON ful.date_id = d.date_id
WHERE ful.order_status IN ('Returned', 'Partial')
GROUP BY d.year, d.quarter, d.month_name, d.month;
GO

-- ══════════════════════════════════════════════════
-- TEST QUERIES
-- ══════════════════════════════════════════════════

-- 1. Grand total leakage by category
SELECT
    leakage_category,
    ROUND(SUM(leakage_amount), 2)           AS total_leakage_tk,
    ROUND(SUM(leakage_amount) * 100.0 /
        SUM(SUM(leakage_amount)) OVER(), 2) AS leakage_pct
FROM vw_total_leakage_summary
GROUP BY leakage_category
ORDER BY total_leakage_tk DESC;

-- 2. Monthly trend — all categories
SELECT
    month_name,
    month_num,
    quarter,
    SUM(CASE WHEN leakage_category = 'Procurement'  THEN leakage_amount ELSE 0 END) AS procurement_tk,
    SUM(CASE WHEN leakage_category = 'Inventory'    THEN leakage_amount ELSE 0 END) AS inventory_tk,
    SUM(CASE WHEN leakage_category = 'Logistics'    THEN leakage_amount ELSE 0 END) AS logistics_tk,
    SUM(CASE WHEN leakage_category = 'Fulfillment'  THEN leakage_amount ELSE 0 END) AS fulfillment_tk,
    ROUND(SUM(leakage_amount), 2)                                                    AS total_monthly_tk
FROM vw_total_leakage_summary
GROUP BY month_name, month_num, quarter
ORDER BY month_num;

-- 3. Quarter summary
SELECT
    quarter,
    leakage_category,
    ROUND(SUM(leakage_amount), 2)           AS quarterly_leakage_tk
FROM vw_total_leakage_summary
GROUP BY quarter, leakage_category
ORDER BY quarter, quarterly_leakage_tk DESC;

-- 4. Grand total — single number
SELECT
    ROUND(SUM(leakage_amount), 2)           AS grand_total_leakage_tk,
    ROUND(SUM(leakage_amount) / 100000, 2)  AS grand_total_lakh
FROM vw_total_leakage_summary;