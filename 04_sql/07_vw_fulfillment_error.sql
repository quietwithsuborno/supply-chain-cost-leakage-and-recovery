

USE BCPL_CostLeakage;
GO

-- ══════════════════════════════════════════════════
-- VIEW: vw_fulfillment_error_cost
-- Purpose: Return + partial shipment cost —
--          order fulfillment leakage identify
-- ══════════════════════════════════════════════════

CREATE VIEW vw_fulfillment_error_cost AS
SELECT
    ful.fulfillment_id,
    ful.fulfillment_date,
    ful.order_status,
    ful.is_return,
    ful.return_reason,
    ful.return_cost,
    ful.is_partial,
    ful.partial_extra_cost,

    -- Total leakage per fulfillment
    ROUND(ful.return_cost + ful.partial_extra_cost, 2)
        AS total_leakage_per_order,

    -- Leakage type label
    CASE
        WHEN ful.is_return  = 1 THEN 'Return'
        WHEN ful.is_partial = 1 THEN 'Partial Shipment'
        ELSE 'No Leakage'
    END AS leakage_type,

    -- PO info
    po.po_id,
    po.order_type,
    po.quantity_ordered,

    -- Product info
    p.product_id,
    p.product_name,
    p.category      AS product_category,

    -- Supplier info
    s.supplier_id,
    s.supplier_name,

    -- Warehouse info
    w.warehouse_id,
    w.warehouse_name,
    w.location      AS warehouse_location,

    -- Date info
    d.month_name,
    d.quarter,
    d.year

FROM fact_order_fulfillment ful
JOIN fact_purchase_orders po ON ful.po_id        = po.po_id
JOIN dim_product          p  ON po.product_id    = p.product_id
JOIN dim_supplier         s  ON po.supplier_id   = s.supplier_id
JOIN dim_warehouse        w  ON ful.warehouse_id = w.warehouse_id
JOIN dim_date             d  ON ful.date_id      = d.date_id
WHERE ful.order_status IN ('Returned', 'Partial');
GO

-- ══════════════════════════════════════════════════
-- TEST QUERIES
-- ══════════════════════════════════════════════════

-- 1. Leakage summary by warehouse
SELECT
    warehouse_name,
    warehouse_location,
    COUNT(fulfillment_id)                           AS error_orders,
    SUM(CAST(is_return AS INT))                     AS returns,
    SUM(CAST(is_partial AS INT))                    AS partials,
    ROUND(SUM(return_cost), 2)                      AS total_return_cost,
    ROUND(SUM(partial_extra_cost), 2)               AS total_partial_cost,
    ROUND(SUM(total_leakage_per_order), 2)          AS total_leakage_tk
FROM vw_fulfillment_error_cost
GROUP BY warehouse_name, warehouse_location
ORDER BY total_leakage_tk DESC;

-- 2. Leakage by type
SELECT
    leakage_type,
    COUNT(fulfillment_id)                       AS order_count,
    ROUND(SUM(total_leakage_per_order), 2)      AS total_leakage_tk,
    ROUND(AVG(total_leakage_per_order), 2)      AS avg_leakage_per_order
FROM vw_fulfillment_error_cost
GROUP BY leakage_type
ORDER BY total_leakage_tk DESC;

-- 3. Return reason breakdown
SELECT
    return_reason,
    COUNT(fulfillment_id)                       AS return_count,
    ROUND(SUM(return_cost), 2)                  AS total_return_cost
FROM vw_fulfillment_error_cost
WHERE is_return = 1
GROUP BY return_reason
ORDER BY return_count DESC;

-- 4. Leakage by product category
SELECT
    product_category,
    COUNT(fulfillment_id)                       AS error_orders,
    ROUND(SUM(total_leakage_per_order), 2)      AS total_leakage_tk
FROM vw_fulfillment_error_cost
GROUP BY product_category
ORDER BY total_leakage_tk DESC;

-- 5. Monthly trend
SELECT
    month_name,
    quarter,
    COUNT(fulfillment_id)                       AS error_orders,
    ROUND(SUM(total_leakage_per_order), 2)      AS monthly_leakage_tk
FROM vw_fulfillment_error_cost
GROUP BY month_name, quarter
ORDER BY quarter, MIN(fulfillment_date);