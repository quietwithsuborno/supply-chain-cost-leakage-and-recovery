USE BCPL_CostLeakage;
GO

-- ══════════════════════════════════════════════════
-- VIEW: vw_procurement_price_variance
-- Purpose: Supplier-wise actual vs standard price
--          gap — procurement leakage identify kora
-- ══════════════════════════════════════════════════

CREATE VIEW vw_procurement_price_variance AS
SELECT
    po.po_id,
    po.order_date,
    po.order_type,
    po.quantity_ordered,
    po.standard_unit_price,
    po.actual_unit_price,

    -- Leakage per unit
    ROUND(po.actual_unit_price - po.standard_unit_price, 2)
        AS price_variance_per_unit,

    -- Leakage % per unit
    ROUND(
        (po.actual_unit_price - po.standard_unit_price)
        / po.standard_unit_price * 100, 2)
        AS variance_pct,

    -- Total leakage for this PO
    ROUND(
        (po.actual_unit_price - po.standard_unit_price)
        * po.quantity_ordered, 2)
        AS total_leakage_amount,

    -- Leakage flag
    CASE
        WHEN ((po.actual_unit_price - po.standard_unit_price)
            / po.standard_unit_price * 100) > 5
        THEN 1 ELSE 0
    END AS is_leakage_flagged,

    -- Supplier info
    s.supplier_id,
    s.supplier_name,
    s.supplier_type,
    s.category      AS supplier_category,

    -- Product info
    p.product_id,
    p.product_name,
    p.category      AS product_category,

    -- Date info
    d.month_name,
    d.quarter,
    d.year

FROM fact_purchase_orders po
JOIN dim_supplier s ON po.supplier_id = s.supplier_id
JOIN dim_product  p ON po.product_id  = p.product_id
JOIN dim_date     d ON po.date_id     = d.date_id
WHERE po.po_status = 'Completed';
GO

-- ══════════════════════════════════════════════════
-- TEST QUERIES
-- ══════════════════════════════════════════════════

-- 1. Total leakage by supplier
SELECT
    supplier_name,
    supplier_type,
    COUNT(po_id)                        AS total_orders,
    ROUND(AVG(variance_pct), 2)         AS avg_variance_pct,
    ROUND(SUM(total_leakage_amount), 2) AS total_leakage_tk
FROM vw_procurement_price_variance
GROUP BY supplier_name, supplier_type
ORDER BY total_leakage_tk DESC;

-- 2. Flagged leakage summary
SELECT
    is_leakage_flagged,
    COUNT(*)                            AS order_count,
    ROUND(SUM(total_leakage_amount), 2) AS total_leakage_tk
FROM vw_procurement_price_variance
GROUP BY is_leakage_flagged;

-- 3. Monthly leakage trend
SELECT
    month_name,
    quarter,
    ROUND(SUM(total_leakage_amount), 2) AS monthly_leakage_tk
FROM vw_procurement_price_variance
WHERE is_leakage_flagged = 1
GROUP BY month_name, quarter
ORDER BY quarter, MIN(order_date);